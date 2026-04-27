import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import pandas as pd
from pandas.tseries.offsets import BDay
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
    """Clase base abstracta para los scrapers de los Diarios Oficiales."""
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
    """Implementación REAL para la Ciudad de México (Afinada con Código Fuente)."""
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
            
            # Buscar todas las tarjetas de iniciativas (articles con clase postcard)
            articulos = soup.find_all('article', class_='postcard')
            
            meses = {
                'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06', 
                'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
            }
            
            for articulo in articulos:
                # 1. Extraer el texto de la iniciativa
                texto_div = articulo.find('div', class_='postcard__preview-txt')
                if not texto_div:
                    continue
                texto_limpio = texto_div.get_text(separator=" ", strip=True)
                
                # 2. Extraer el enlace
                enlace_tag = articulo.find('a', href=True)
                if enlace_tag:
                    href = enlace_tag['href']
                    enlace = self.base_url + href if href.startswith('/') else href
                else:
                    enlace = self.url
                    
                # 3. Extraer la fecha y darle formato correcto (YYYY-MM-DD)
                fecha_formateada = datetime.now().strftime("%Y-%m-%d")
                time_tag = articulo.find('time')
                
                if time_tag:
                    fecha_texto = time_tag.get_text(strip=True).lower()
                    # Busca el formato: 23 abr 2026
                    match = re.search(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})', fecha_texto)
                    if match:
                        dia, mes_texto, anio = match.groups()
                        # Toma las primeras 3 letras del mes y lo busca en el diccionario
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

def get_all_scraped_data() -> pd.DataFrame:
    """Ejecuta todos los scrapers reales."""
    data = []
    
    scraper_gto = ScraperGuanajuato()
    scraper_nl = ScraperNuevoLeon()
    scraper_ags = ScraperAguascalientes() 
    scraper_tab = ScraperTabasco() 
    scraper_bc = ScraperBajaCalifornia() 
    scraper_bcs = ScraperBajaCaliforniaSur()
    scraper_fed = ScraperFederacion() 
    scraper_cdmx = ScraperCDMX() # Instanciamos la CDMX
    
    data.extend(scraper_gto.scrape())
    data.extend(scraper_nl.scrape())
    data.extend(scraper_ags.scrape()) 
    data.extend(scraper_tab.scrape()) 
    data.extend(scraper_bc.scrape()) 
    data.extend(scraper_bcs.scrape()) 
    data.extend(scraper_fed.scrape()) 
    data.extend(scraper_cdmx.scrape()) # Ejecutamos a la CDMX
    
    if len(data) == 0:
        return pd.DataFrame(columns=["Estado", "Fecha", "Texto Extraído", "Enlace"])
        
    df = pd.DataFrame(data)
    
    # --- FILTRO DE LOS ÚLTIMOS 5 DÍAS HÁBILES ---
    df['Fecha_Parseada'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    hoy = pd.Timestamp.today().normalize()
    fecha_corte = hoy - BDay(5)
    
    df_filtrado = df[(df['Fecha_Parseada'] >= fecha_corte) | (df['Fecha_Parseada'].isna())].copy()
    df_filtrado.drop(columns=['Fecha_Parseada'], inplace=True)
    
    if df_filtrado.empty:
        return pd.DataFrame(columns=["Estado", "Fecha", "Texto Extraído", "Enlace"])
        
    return df_filtrado
