import re
import pandas as pd

def es_relevante_palabras_clave(text: str) -> bool:
    """
    Filtro basado en la lista de palabras clave proporcionada.
    """
    text_lower = text.lower()
    
    # Lista de palabras clave (se incluyen plurales para mayor precisión)
    regex_claves = r'\b(penal|penales|nna|niña|niñas|niño|niños|adolescente|adolescentes|adopción|adopciones)\b'
    
    if re.search(regex_claves, text_lower):
        return True
    return False

def classify_severity(text: str) -> tuple:
    """
    Analiza un fragmento de texto legal utilizando reglas básicas (Regex)
    para determinar si hay un aumento, disminución, o creación de penas/delitos.
    """
    # Primero pasamos el nuevo filtro. Si no cumple, se descarta.
    if not es_relevante_palabras_clave(text):
        return 'Fuera de Enfoque', 0

    text_lower = text.lower()
    
    # Expresiones regulares para diferentes escenarios
    regex_aumento = r'\b(aumenta|incrementa|agrava|adiciona|endurece)\b.*\b(pena|prisión|sanción|multa|años)\b'
    regex_disminucion = r'\b(disminuye|reduce|atenúa|mitiga)\b.*\b(pena|prisión|sanción|multa|años)\b'
    regex_creacion = r'\b(crea|tipifica|nuevo)\b.*\b(delito|crimen|tipo penal)\b'
    regex_derogacion = r'\b(deroga|abroga|elimina)\b.*\b(artículo|delito|pena)\b'
    
    # Evaluación en orden de prioridad
    if re.search(regex_aumento, text_lower):
        return 'Aumento de Pena', 1
    elif re.search(regex_disminucion, text_lower):
        return 'Disminución de Pena', -1
    elif re.search(regex_creacion, text_lower):
        return 'Creación de Nuevo Delito', 1
    elif re.search(regex_derogacion, text_lower):
        return 'Derogación', -1
    else:
        return 'Neutral', 0

def process_dataframe_nlp(df):
    """
    Aplica la clasificación NLP a un DataFrame entero.
    """
    if df.empty:
        return df
        
    df[['Clasificación', 'Severidad']] = df['Texto Extraído'].apply(
        lambda x: pd.Series(classify_severity(x))
    )
    return df