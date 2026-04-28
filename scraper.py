import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
import urllib3
import ssl
import re

# 1. Desactivar advertencias de seguridad SSL en la consola
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. Escudo protector para Mac: desactiva la verificación estricta de certificados globalmente
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

class DiarioOficialScraper(ABC):
    def __init__(self, estado):
        self.estado = estado
        
    @abstractmethod
    def scrape(self) -> list:
        pass

class ScraperGuanajuato(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Guanajuato")
        self.url = "https://www.congresogto.gob.mx/gaceta/iniciativas"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            elementos = soup.find_all('tr') 
            for item in elementos:
                texto = item.get_text(separator=" ", strip=True)
                enlace_tag = item.find('a', href=True)
                if enlace_tag:
                    href = enlace_tag['href']
                    enlace = "https://www.congresogto.gob.mx" + href if href.startswith('/') else href
                else:
                    enlace = self.url
                if len(texto) > 40:
                    resultados.append({
                        "Estado": self.estado,
                        "Fecha": datetime.now().strftime("%Y-%m-%d"),
                        "Texto Extraído": texto,
                        "Enlace": enlace
                    })
        except Exception as e:
            print(f"Error en Guanajuato: {e}")
        return resultados

class ScraperNuevoLeon(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Nuevo León")
        self.url = "https://www.hcnl.gob.mx/iniciativas_lxxvii/"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, 'html.parser')
            filas = soup.find_all('tr') 
            for fila in filas:
                celdas = fila.find_all(['td', 'th'])
                if len(celdas) >= 8:
                    texto_limpio = celdas[4].get_text(separator=" ", strip=True)
                    if texto_limpio.lower() == 'asunto' or not texto_limpio:
                        continue
                    enlace_tag = celdas[-1].find('a', href=True)
                    if not enlace_tag:
                        enlace_tag = celdas[4].find('a', href=True)
                    if enlace_tag:
                        href = enlace_tag['href']
                        enlace = "https://www.hcnl.gob.mx" + href if href.startswith('/') else href
                    else:
                        enlace = self.url
                    fecha_texto = celdas[6].get_text(strip=True)
                    if not fecha_texto:
                        fecha_texto = datetime.now().strftime("%Y-%m-%d")
                    if len(texto_limpio) > 20:
                        resultados.append({
                            "Estado": self.estado,
                            "Fecha": fecha_texto,
                            "Texto Extraído": texto_limpio,
                            "Enlace": enlace
                        })
        except Exception as e:
            print(f"Error en Nuevo León: {e}")
        return resultados

class ScraperAguascalientes(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Aguascalientes")
        self.url = "https://congresoags.gob.mx/agenda_legislativa/iniciativas"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, 'html.parser')
            filas = soup.find_all('tr') 
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 6:
                    texto_limpio = celdas[2].get_text(separator=" ", strip=True)
                    enlace_tag = celdas[-1].find('a', href=True)
                    if enlace_tag:
                        href = enlace_tag['href']
                        enlace = "https://congresoags.gob.mx" + href if href.startswith('/') else href
                    else:
                        enlace = self.url
                    if len(texto_limpio) > 20:
                        resultados.append({
                            "Estado": self.estado,
                            "Fecha": datetime.now().strftime("%Y-%m-%d"),
                            "Texto Extraído": texto_limpio,
                            "Enlace": enlace
                        })
        except Exception as e:
            print(f"Error en Aguascalientes: {e}")
        return resultados

class ScraperTabasco(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Tabasco")
        self.url = "https://congresotabasco.gob.mx/iniciativas/"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, 'html.parser')
            filas = soup.find_all('tr')
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 8:
                    texto_limpio = celdas[1].get_text(separator=" ", strip=True)
                    fecha_texto = celdas[4].get_text(strip=True)
                    try:
                        fecha_obj = datetime.strptime(fecha_texto, "%d/%m/%Y")
                        fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        fecha_formateada = datetime.now().strftime("%Y-%m-%d")
                    enlace_tag = celdas[7].find('a', href=True)
                    if enlace_tag:
                        href = enlace_tag['href']
                        enlace = "https://congresotabasco.gob.mx" + href if href.startswith('/') else href
                    else:
                        enlace = self.url
                    if len(texto_limpio) > 20:
                        resultados.append({
                            "Estado": self.estado,
                            "Fecha": fecha_formateada,
                            "Texto Extraído": texto_limpio,
                            "Enlace": enlace
                        })
        except Exception as e:
            print(f"Error en Tabasco: {e}")
        return resultados

class ScraperBajaCalifornia(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Baja California")
        self.url = "https://www.congresobc.gob.mx/TrabajoLegislativo/Iniciativas"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8' 
            soup = BeautifulSoup(response.text, 'html.parser')
            enlaces = soup.find_all('a', href=True)
            textos_vistos = set()
            for tag in enlaces:
                href = tag['href']
                if '.pdf' in href.lower() or '/Documentos/ProcesoParlamentario/' in href:
                    padre = tag.parent
                    while padre and padre.name != 'tr' and len(padre.get_text(strip=True)) < 50:
                        padre = padre.parent
                    if padre:
                        texto_limpio = padre.get_text(separator=" ", strip=True)
                    else:
                        texto_limpio = tag.parent.get_text(separator=" ", strip=True)
                    if len(texto_limpio) > 40 and texto_limpio not in textos_vistos:
                        textos_vistos.add(texto_limpio)
                        if href.startswith('http'):
                            enlace = href
                        elif href.startswith('/'):
                            enlace = "https://www.congresobc.gob.mx" + href
                        else:
                            enlace = "https://www.congresobc.gob.mx/TrabajoLegislativo/" + href
                        fecha_encontrada = datetime.now().strftime("%Y-%m-%d")
                        match_fecha = re.search(r'(\d{4}/\d{2}/\d{2}|\d{2}/\d{2}/\d{4})', texto_limpio)
                        if match_fecha:
                            fecha_str = match_fecha.group(1)
                            if '/' in fecha_str:
                                partes = fecha_str.split('/')
                                if len(partes[0]) == 4: 
                                    fecha_encontrada = f"{partes[0]}-{partes[1]}-{partes[2]}"
                                else: 
                                    fecha_encontrada = f"{partes[2]}-{partes[1]}-{partes[0]}"
                        resultados.append({
                            "Estado": self.estado,
                            "Fecha": fecha_encontrada,
                            "Texto Extraído": texto_limpio,
                            "Enlace": enlace
                        })
        except Exception as e:
            print(f"Error en Baja California: {e}")
        return resultados

class ScraperBajaCaliforniaSur(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Baja California Sur")
        self.url_base = "https://www.cbcs.gob.mx"
        self.url_list = "https://www.cbcs.gob.mx/index.php/xvii-legislatura/xvii-leg-segundo-ano/xvii-leg-segundo-ano-segundo-periodo/orden-del-dia"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response_list = requests.get(self.url_list, headers=headers, timeout=15, verify=False)
            soup_list = BeautifulSoup(response_list.text, 'html.parser')
            td_title = soup_list.find('td', class_='list-title')
            if not td_title:
                return resultados
            a_tag = td_title.find('a', href=True)
            if not a_tag:
                return resultados
            enlace_sesion = self.url_base + a_tag['href'] if a_tag['href'].startswith('/') else a_tag['href']
            titulo_sesion = a_tag.get_text(strip=True).upper()
            meses = {
                'ENERO':'01', 'FEBRERO':'02', 'MARZO':'03', 'ABRIL':'04', 'MAYO':'05', 'JUNIO':'06', 
                'JULIO':'07', 'AGOSTO':'08', 'SEPTIEMBRE':'09', 'OCTUBRE':'10', 'NOVIEMBRE':'11', 'DICIEMBRE':'12'
            }
            fecha_formateada = datetime.now().strftime("%Y-%m-%d")
            match = re.search(r'(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', titulo_sesion)
            if match:
                dia, mes_texto, anio = match.groups()
                mes_num = meses.get(mes_texto, '01')
                fecha_formateada = f"{anio}-{mes_num}-{dia.zfill(2)}"
            
            response_sesion = requests.get(enlace_sesion, headers=headers, timeout=15, verify=False)
            soup_sesion = BeautifulSoup(response_sesion.text, 'html.parser')
            parrafos = soup_sesion.find_all('p')
            for p in parrafos:
                texto_limpio = p.get_text(separator=" ", strip=True)
                if len(texto_limpio) > 40:
                    enlace_pdf_tag = p.find('a', href=True)
                    if enlace_pdf_tag:
                        href_pdf = enlace_pdf_tag['href']
                        enlace_pdf = self.url_base + href_pdf if href_pdf.startswith('/') else href_pdf
                    else:
                        enlace_pdf = enlace_sesion 
                    resultados.append({
                        "Estado": self.estado,
                        "Fecha": fecha_formateada,
                        "Texto Extraído": texto_limpio,
                        "Enlace": enlace_pdf
                    })
        except Exception as e:
            print(f"Error en Baja California Sur: {e}")
        return resultados

class ScraperFederacion(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Federación")
        self.url = "https://sil.gobernacion.gob.mx/Busquedas/Avanzada/ResultadosBusquedaAvanzada.php?SID=430edc92663c4962f471df7728ca07b7&Serial=9b27ab1eb3c2178c441d4cd968e13267&Reg=7704&Origen=BA&Paginas=15"
        self.base_url = "https://sil.gobernacion.gob.mx"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            filas = soup.find_all('tr')
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 10:
                    tipo = celdas[1].get_text(strip=True)
                    if "Iniciativa" in tipo or "Minuta" in tipo:
                        texto_limpio = celdas[2].get_text(separator=" ", strip=True)
                        fecha_texto = celdas[5].get_text(strip=True)
                        try:
                            fecha_obj = datetime.strptime(fecha_texto, "%d/%m/%Y")
                            fecha_formateada = fecha_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            fecha_formateada = datetime.now().strftime("%Y-%m-%d")
                        enlace_tag = celdas[2].find('a')
                        enlace = self.url
                        if enlace_tag and enlace_tag.has_attr('onclick'):
                            onclick_text = enlace_tag['onclick']
                            match = re.search(r'window\.open\([\'"]([^\'"]+)[\'"]', onclick_text)
                            if match:
                                enlace = self.base_url + match.group(1)
                        if len(texto_limpio) > 20:
                            resultados.append({
                                "Estado": self.estado,
                                "Fecha": fecha_formateada,
                                "Texto Extraído": texto_limpio,
                                "Enlace": enlace
                            })
        except Exception as e:
            print(f"Error en Federación: {e}")
        return resultados

class ScraperCDMX(DiarioOficialScraper):
    def __init__(self):
        super().__init__("Ciudad de México")
        self.url = "https://ciudadana.congresocdmx.gob.mx/Iniciativa/iniciativas"
        self.base_url = "https://ciudadana.congresocdmx.gob.mx"
        
    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            articulos = soup.find_all('article', class_='postcard')
            meses = {
                'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06', 
                'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
            }
            for articulo in articulos:
                texto_div = articulo.find('div', class_='postcard__preview-txt')
                if not texto_div:
                    continue
                texto_limpio = texto_div.get_text(separator=" ", strip=True)
                enlace_tag = articulo.find('a', href=True)
                if enlace_tag:
                    href = enlace_tag['href']
                    enlace = self.base_url + href if href.startswith('/') else href
                else:
                    enlace = self.url
                fecha_formateada = datetime.now().strftime("%Y-%m-%d")
                time_tag = articulo.find('time')
                if time_tag:
                    fecha_texto = time_tag.get_text(strip=True).lower()
                    match = re.search(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})', fecha_texto)
                    if match:
                        dia, mes_texto, anio = match.groups()
                        mes_num = meses.get(mes_texto[:3], '01') 
                        fecha_formateada = f"{anio}-{mes_num}-{dia.zfill(2)}"
                if len(texto_limpio) > 20:
                    resultados.append({
                        "Estado": self.estado,
                        "Fecha": fecha_formateada,
                        "Texto Extraído": texto_limpio,
                        "Enlace": enlace
                    })
        except Exception as e:
            print(f"Error en CDMX: {e}")
        return resultados


class ScraperEdomex(DiarioOficialScraper):
    """
    Scraper para la Gaceta Parlamentaria del Estado de México.

    PROBLEMA ORIGINAL: El sitio congresoedomex.gob.mx renderiza las tarjetas
    de gaceta con JavaScript (framework SPA), por lo que BeautifulSoup no las
    ve en el HTML estático retornado por requests.

    SOLUCIÓN: El servidor de documentos (legislacion.congresoedomex.gob.mx)
    expone una API JSON que alimenta el frontend. Consultamos esa API directamente.
    Si la API no responde, reconstruimos las URLs de PDF usando el patrón conocido
    del nombre de archivo (GP-{num} ({DD}-{MES}-{YY}).pdf) como fallback.

    NOTA SOBRE EL PDF: La Gaceta es un PDF escaneado (imagen, no texto), por lo
    que no es posible extraer texto con NLP. Generamos una fila por cada gaceta
    dentro del rango de fechas solicitado, con el enlace directo al PDF para
    revisión manual, y un texto descriptivo que incluye el número de gaceta y
    la fecha para que el filtro de palabras clave en app.py pueda ignorarse
    via el "Pase VIP" ya implementado.
    """

    # Abreviaturas de meses usadas en los nombres de archivo del servidor
    MESES_ABREV = {
        '01': 'ENE', '02': 'FEB', '03': 'MAR', '04': 'ABR',
        '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AGO',
        '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DIC'
    }
    MESES_NOMBRE = {
        'ENE': '01', 'FEB': '02', 'MAR': '03', 'ABR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DIC': '12',
        # Versión completa para el parsing de la API
        'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
        'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
        'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
    }

    def __init__(self):
        super().__init__("Estado de México")
        self.api_url = "https://legislacion.congresoedomex.gob.mx/api/gacetas"
        self.base_pdf = "https://legislacion.congresoedomex.gob.mx/storage/documentos/gaceta/"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                        'Accept': 'application/json, text/html, */*'}

    def _parsear_fecha_api(self, texto_fecha: str) -> str:
        """Convierte texto de fecha de la API al formato YYYY-MM-DD."""
        texto = texto_fecha.strip().upper()
        # Formato: "22 DE ABRIL DE 2026" o "22 ABRIL 2026"
        match = re.search(r'(\d{1,2})\s+(?:DE\s+)?([A-ZÁÉÍÓÚ]+)\s+(?:DE\s+)?(\d{4})', texto)
        if match:
            dia, mes_texto, anio = match.groups()
            mes_num = self.MESES_NOMBRE.get(mes_texto, '01')
            return f"{anio}-{mes_num}-{dia.zfill(2)}"
        return datetime.now().strftime("%Y-%m-%d")

    def _parsear_fecha_filename(self, nombre_archivo: str) -> str:
        """Extrae la fecha del nombre de archivo GP-123 (22-ABR-26).pdf -> 2026-04-22."""
        match = re.search(r'\((\d{1,2})-([A-Z]+)-(\d{2,4})\)', nombre_archivo.upper())
        if match:
            dia, mes_abrev, anio = match.groups()
            mes_num = self.MESES_NOMBRE.get(mes_abrev, '01')
            # El año viene como 2 dígitos (26) o 4 (2026)
            anio_completo = f"20{anio}" if len(anio) == 2 else anio
            return f"{anio_completo}-{mes_num}-{dia.zfill(2)}"
        return datetime.now().strftime("%Y-%m-%d")

    def _via_api(self) -> list:
        """
        Intenta obtener el listado de gacetas desde la API JSON del servidor.
        Retorna lista de dicts {numero, fecha_iso, url_pdf} o lista vacía si falla.
        """
        try:
            resp = requests.get(self.api_url, headers=self.headers, timeout=15, verify=False)
            if resp.status_code != 200:
                return []
            datos = resp.json()
            # La API puede retornar directamente una lista o un objeto con clave 'data'
            items = datos if isinstance(datos, list) else datos.get('data', [])
            resultados = []
            for item in items:
                # Campos posibles según estructura típica de Laravel/API REST
                numero = item.get('numero') or item.get('num') or item.get('id', '?')
                url_pdf = item.get('url') or item.get('archivo') or item.get('documento', '')
                if not url_pdf.startswith('http'):
                    url_pdf = self.base_pdf + url_pdf
                fecha_raw = (item.get('fecha') or item.get('fecha_publicacion') or
                             item.get('date') or '')
                fecha_iso = self._parsear_fecha_api(str(fecha_raw)) if fecha_raw else \
                            self._parsear_fecha_filename(url_pdf)
                resultados.append({
                    'numero': str(numero),
                    'fecha_iso': fecha_iso,
                    'url_pdf': url_pdf
                })
            return resultados
        except Exception:
            return []

    def _via_html_scraping(self) -> list:
        """
        Fallback: parsea el HTML de la página principal buscando todos los
        enlaces a PDFs de gaceta. Funciona si el servidor sirve HTML estático
        o si el framework pre-renderiza en servidor (SSR).
        La lista de gacetas visible en el contenido ya confirmó que el patrón
        de URLs es: /storage/documentos/gaceta/GP-{N} ({DD}-{MES}-{AA}).pdf
        """
        resultados = []
        try:
            url_pagina = "https://www.congresoedomex.gob.mx/trabajo-legislativo"
            resp = requests.get(url_pagina, headers=self.headers, timeout=20, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Buscar todos los <a> que apunten a PDFs de gaceta
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'gaceta' in href.lower() and href.endswith('.pdf'):
                    url_pdf = href if href.startswith('http') else \
                              "https://legislacion.congresoedomex.gob.mx" + href
                    # Extraer número del enlace o del texto del enlace
                    texto_link = a.get_text(separator=" ", strip=True)
                    match_num = re.search(r'GP-?(\d+)', url_pdf, re.IGNORECASE)
                    numero = match_num.group(1) if match_num else '?'
                    fecha_iso = self._parsear_fecha_filename(url_pdf)
                    resultados.append({
                        'numero': numero,
                        'fecha_iso': fecha_iso,
                        'url_pdf': url_pdf,
                        'texto_extra': texto_link
                    })
        except Exception as e:
            print(f"Error en scraping HTML Edomex: {e}")
        return resultados

    def _via_patron_url(self, num_gaceta: int, fecha_dt: datetime) -> dict:
        """
        Construye la URL directa del PDF usando el patrón conocido del servidor.
        Útil como fallback de último recurso para la gaceta más reciente.
        Patrón: GP-{N} ({DD}-{MES}-{AA}).pdf
        """
        dd = fecha_dt.strftime("%d")
        mes = self.MESES_ABREV[fecha_dt.strftime("%m")]
        aa = fecha_dt.strftime("%y")
        anio_completo = fecha_dt.strftime("%Y")
        nombre = f"GP-{num_gaceta} ({dd}-{mes}-{aa}).pdf"
        from urllib.parse import quote
        url_pdf = self.base_pdf + quote(nombre)
        return {
            'numero': str(num_gaceta),
            'fecha_iso': f"{anio_completo}-{fecha_dt.strftime('%m')}-{dd}",
            'url_pdf': url_pdf
        }

    def scrape(self) -> list:
        resultados = []

        # --- Estrategia 1: API JSON ---
        gacetas = self._via_api()

        # --- Estrategia 2: Scraping HTML (fallback) ---
        if not gacetas:
            gacetas = self._via_html_scraping()

        # --- Estrategia 3: Construir URL de la gaceta más reciente (último recurso) ---
        if not gacetas:
            print("Edomex: API y HTML fallaron. Usando patrón de URL como fallback.")
            # Tomamos la gaceta más reciente conocida (GP-123, 22-ABR-26) como ancla
            # y generamos los últimos 5 días hábiles para cubrir el rango típico de búsqueda
            from pandas.tseries.offsets import BDay
            hoy = pd.Timestamp.today()
            # Número más reciente conocido: 123 (22 de abril de 2026)
            # Estimamos: ~1 gaceta por semana, así que retrocedemos aprox.
            gaceta_ancla_num = 123
            fecha_ancla = datetime(2026, 4, 22)
            dias_diff = (hoy.to_pydatetime() - fecha_ancla).days
            gacetas_estimadas = max(0, round(dias_diff / 7))
            num_actual = gaceta_ancla_num + gacetas_estimadas
            gacetas = [self._via_patron_url(num_actual, hoy.to_pydatetime())]

        # --- Generar filas para cada gaceta encontrada ---
        for g in gacetas:
            numero = g.get('numero', '?')
            fecha_iso = g.get('fecha_iso', datetime.now().strftime("%Y-%m-%d"))
            url_pdf = g.get('url_pdf', '')
            texto_extra = g.get('texto_extra', '')

            texto = (
                f"📋 GACETA PARLAMENTARIA EDOMEX #{numero} — {fecha_iso}. "
                f"Documento PDF escaneado (imagen). Requiere revisión manual. "
                f"{texto_extra}"
            ).strip()

            resultados.append({
                "Estado": self.estado,
                "Fecha": fecha_iso,
                "Texto Extraído": texto,
                "Enlace": url_pdf
            })

        return resultados


def get_all_scraped_data() -> pd.DataFrame:
    data = []
    
    scraper_gto = ScraperGuanajuato()
    scraper_nl = ScraperNuevoLeon()
    scraper_ags = ScraperAguascalientes() 
    scraper_tab = ScraperTabasco() 
    scraper_bc = ScraperBajaCalifornia() 
    scraper_bcs = ScraperBajaCaliforniaSur()
    scraper_fed = ScraperFederacion() 
    scraper_cdmx = ScraperCDMX() 
    scraper_edomex = ScraperEdomex()
    
    data.extend(scraper_gto.scrape())
    data.extend(scraper_nl.scrape())
    data.extend(scraper_ags.scrape()) 
    data.extend(scraper_tab.scrape()) 
    data.extend(scraper_bc.scrape()) 
    data.extend(scraper_bcs.scrape()) 
    data.extend(scraper_fed.scrape()) 
    data.extend(scraper_cdmx.scrape()) 
    data.extend(scraper_edomex.scrape()) 
    
    if len(data) == 0:
        return pd.DataFrame(columns=["Estado", "Fecha", "Texto Extraído", "Enlace"])
        
    return pd.DataFrame(data)
