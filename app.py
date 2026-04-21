import streamlit as st
import pandas as pd
import plotly.express as px
import re
import scraper
import nlp

# Coordenadas exactas de los estados para ubicarlos en el mapa
COORDENADAS_ESTADOS = {
    "Aguascalientes": {"lat": 21.8853, "lon": -102.2916},
    "Baja California": {"lat": 30.8406, "lon": -115.2838},
    "Baja California Sur": {"lat": 26.0444, "lon": -111.1666},
    "Guanajuato": {"lat": 21.0190, "lon": -101.2574},
    "Nuevo León": {"lat": 25.5922, "lon": -99.9962},
    "Tabasco": {"lat": 17.8409, "lon": -92.6180}
}

# 1. Configuración de la página y Título
st.set_page_config(page_title="Monitor de reformas", page_icon="⚖️", layout="wide")
st.title("Monitor de reformas")

# 2. Variable de estado para controlar el botón de inicio
if "busqueda_iniciada" not in st.session_state:
    st.session_state.busqueda_iniciada = False

# 3. --- PANEL DE CONTROL Y FILTROS (BARRA LATERAL) ---
st.sidebar.header("⚙️ Panel de Control")

with st.sidebar.form(key='search_form'):
    # Filtro de Estados
    estados_lista = ["Aguascalientes", "Baja California", "Baja California Sur", "Guanajuato", "Nuevo León", "Tabasco"]
    estado_filtro = st.multiselect("1. Selecciona Estados:", options=estados_lista, default=estados_lista)
    
    # Filtro de Palabras Clave (Predefinidas)
    opciones_palabras = [
        "Penal", "NNA", "Niña", "Niño", "Adolescente", 
        "Adopción", "Salud", 
        "Seguridad", "Constitución", "Educación", "Presupuesto"
    ]
    palabras_seleccionadas = st.multiselect(
        "2. Elige palabras clave:", 
        options=opciones_palabras, 
        default=["Penal", "NNA", "Niña", "Niño", "Adolescente", "Adopción"]
    )
    
    # Filtro de Palabras Clave (Manuales)
    palabras_extra = st.text_input("3. O ingresa nuevas (separadas por coma):", placeholder="Ej. civil, violencia, fraude...")
    
    # Botón maestro para arrancar
    st.write("") # Espacio en blanco
    submit_button = st.form_submit_button(label="Empezar Búsqueda 🚀")

# Si el usuario presiona el botón, cambiamos el estado a True
if submit_button:
    st.session_state.busqueda_iniciada = True

# 4. Función de Extracción 
@st.cache_data(ttl=3600) 
def load_and_process_data():
    df = scraper.get_all_scraped_data()
    if df.empty:
        return pd.DataFrame(columns=["Estado", "Fecha", "Texto Extraído", "Enlace", "Clasificación", "Severidad"])
    
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = nlp.process_dataframe_nlp(df) # Mantenemos el NLP para medir severidad
    return df

# 5. --- LÓGICA PRINCIPAL AL INICIAR BÚSQUEDA ---
if st.session_state.busqueda_iniciada:
    with st.spinner('Extrayendo datos y aplicando tus filtros. Esto puede tomar unos segundos...'):
        df_main = load_and_process_data()
        
    if df_main.empty or len(df_main) == 0:
        st.warning("No se encontraron iniciativas en este momento o hubo un bloqueo temporal de red. Intenta de nuevo más tarde.")
    else:
        # A) Filtramos por los estados que eligió el usuario
        df_filtrado = df_main[df_main['Estado'].isin(estado_filtro)]
        
        # B) Consolidamos todas las palabras clave (las del menú + las escritas a mano)
        lista_completa_palabras = palabras_seleccionadas.copy()
        if palabras_extra:
            # Limpiamos los espacios extras de las palabras escritas a mano
            palabras_extra_limpias = [p.strip() for p in palabras_extra.split(",") if p.strip()]
            lista_completa_palabras.extend(palabras_extra_limpias)
        
        # C) Aplicamos el filtro de palabras clave en el texto extraído
        if lista_completa_palabras:
            # Creamos un patrón matemático (Regex) que busque cualquier palabra de la lista
            patron_regex = '|'.join([re.escape(p) for p in lista_completa_palabras])
            # case=False hace que no importe si está en mayúsculas o minúsculas
            df_relevante = df_filtrado[df_filtrado['Texto Extraído'].str.contains(patron_regex, case=False, na=False)].copy()
        else:
            df_relevante = df_filtrado.copy()

        # --- SECCIÓN DE RESULTADOS VISUALES ---
        col1, col2 = st.columns(2)
        col1.metric("Publicaciones Totales Extraídas", len(df_filtrado))
        col2.metric("Iniciativas que coinciden con tus palabras", len(df_relevante))

        # --- MAPA DE CALOR ---
        st.divider()
        st.subheader("🗺️ Mapa de Impacto Territorial")
        
        if not df_relevante.empty:
            # Aseguramos que exista la columna Severidad para que el mapa no falle
            if 'Severidad' not in df_relevante.columns:
                df_relevante['Severidad'] = 0
                
            # Agrupamos los datos para el mapa
            df_mapa = df_relevante.groupby('Estado').agg({'Severidad': 'sum', 'Texto Extraído': 'count'}).reset_index()
            df_mapa.rename(columns={'Texto Extraído': 'Total Iniciativas'}, inplace=True)
            
            # Asignamos coordenadas
            df_mapa['lat'] = df_mapa['Estado'].map(lambda x: COORDENADAS_ESTADOS.get(x, {}).get('lat', 23.6345))
            df_mapa['lon'] = df_mapa['Estado'].map(lambda x: COORDENADAS_ESTADOS.get(x, {}).get('lon', -102.5528))

            # Dibujamos el mapa
            fig = px.scatter_geo(
                df_mapa,
                lat='lat',
                lon='lon',
                size='Total Iniciativas',
                color='Severidad',
                hover_name='Estado',
                color_continuous_scale=px.colors.diverging.RdBu_r,
                color_continuous_midpoint=0,
                scope='north america',
                title='El tamaño del círculo indica la cantidad de iniciativas; el color indica la severidad.'
            )
            
            fig.update_geos(fitbounds="locations", visible=False, showcountries=True, countrycolor="Black", showsubunits=True, subunitcolor="Gray")
            st.plotly_chart(fig)
        else:
            st.info("No hay iniciativas que coincidan con las palabras clave ingresadas.")

        # --- TABLA DE DATOS DETALLADOS ---
        st.divider()
        st.subheader("📄 Registro de Iniciativas")

        if not df_relevante.empty:
            st.dataframe(
                df_relevante.sort_values(by="Fecha", ascending=False),
                column_config={
                    "Enlace": st.column_config.LinkColumn("Enlace Fuente"),
                    "Severidad": st.column_config.NumberColumn(
                        "Impacto",
                        help="1 = Aumento, -1 = Disminución, 0 = Neutral"
                    )
                },
                hide_index=True
            )
else:
    # Pantalla de bienvenida antes de apretar el botón
    st.info("👈 **Configura tus filtros en el menú lateral** y haz clic en **'Empezar Búsqueda 🚀'** para comenzar a analizar los Diarios Oficiales.")