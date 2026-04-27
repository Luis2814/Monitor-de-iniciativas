import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import pandas as pd
from pandas.tseries.offsets import BDay
from datetime import datetime
import urllib3
import ssl
import re
import io
import PyPDF2

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
    """Implementación Lector de PDFs para el Estado de México."""
    def __init__(self):
        super().__init__("Estado de México")
        self.url = "https://www.congresoedomex.gob.mx/trabajo-legislativo"

    def scrape(self):
        resultados = []
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(self.url, headers=headers, timeout=15, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Buscamos la última gaceta disponible (la primera tarjeta)
            gaceta_card = soup.find('a', class_='gaceta-card-link')
            if not gaceta_card:
                return resultados

            enlace_pdf = gaceta_card['href']

            # 2. Extraer la fecha de la tarjeta
            fecha_formateada = datetime.now().strftime("%Y-%m-%d")
            fecha_tag = gaceta_card.find('div', class_='gaceta-fecha')
            
            if fecha_tag:
                texto_fecha = fecha_tag.get_text(strip=True).lower()
                meses = {
                    'enero':'01', 'febrero':'02', 'marzo':'03', 'abril':'04', 'mayo':'05', 'junio':'06',
                    'julio':'07', 'agosto':'08', 'septiembre':'09', 'octubre':'10', 'noviembre':'11', 'diciembre':'12'
                }
                match = re.search(r'(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})', texto_fecha)
                if match:
                    dia, mes_texto, anio = match.groups()
                    mes_num = meses.get(mes_texto, '01')
                    fecha_formateada = f"{anio}-{mes_num}-{dia.zfill(2)}"

            # 3. Magia: Descargar y leer el PDF en memoria invisible
            res_pdf = requests.get(enlace_pdf, headers=headers, timeout=25, verify=False)
            lector = PyPDF2.PdfReader(io.BytesIO(res_pdf.content))

            # Leer SOLO las primeras 10 páginas (para no saturar la memoria, aquí suele estar el índice)
            texto_completo = ""
            limite_paginas = min(10, len(lector.pages))
            for i in range(limite_paginas):
                pag = lector.pages[i].extract_text()
                if pag:
                    texto_completo += pag + " "

            # 4. Dividir el documento cada vez que mencione la palabra "Iniciativa"
            # Captura patrones como: "Iniciativa con proyecto de...", "Iniciativa de ley..."
            fragmentos = re.split(r'(?i)(Iniciativa\s+con\s+proyecto|Iniciativa\s+de\s+ley|Iniciativa\s+de\s+decreto|Iniciativa\s+formulada)', texto_completo)

            if len(fragmentos) > 1:
                # Extraemos el título capturado y un fragmento de texto siguiente
                for i in range(1, len(fragmentos), 2):
                    titulo_encontrado = fragmentos[i]
                    contenido_asociado = fragmentos[i+1][:400] # Tomamos los siguientes 400 caracteres como contexto
                    texto_iniciativa = f"{titulo_encontrado} {contenido_asociado}".strip()
                    
                    # Limpiamos los saltos de línea raros del PDF
                    texto_iniciativa = re.sub(r'\s+', ' ', texto_iniciativa) 

                    if len(texto_iniciativa) > 40:
                        resultados.append({
                            "Estado": self.estado,
                            "Fecha": fecha_formateada,
                            "Texto Extraído": texto_iniciativa,
                            "Enlace": enlace_pdf
                        })
            else:
                # Si por alguna razón el índice no dice "Iniciativa", mandamos un resumen general de la gaceta
                resultados.append({
                    "Estado": self.estado,
                    "Fecha": fecha_formateada,
                    "Texto Extraído": f"Gaceta Parlamentaria (Resumen General): {texto_completo[:600]}...",
                    "Enlace": enlace_pdf
                })

        except Exception as e:
            print(f"Error en Estado de México: {e}")

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
    scraper_cdmx = ScraperCDMX() 
    scraper_edomex = ScraperEdomex() # Instanciamos Edomex
    
    data.extend(scraper_gto.scrape())
    data.extend(scraper_nl.scrape())
    data.extend(scraper_ags.scrape()) 
    data.extend(scraper_tab.scrape()) 
    data.extend(scraper_bc.scrape()) 
    data.extend(scraper_bcs.scrape()) 
    data.extend(scraper_fed.scrape()) 
    data.extend(scraper_cdmx.scrape()) 
    data.extend(scraper_edomex.scrape()) # Ejecutamos Edomex
    
    if len(data) == 0:
        return pd.DataFrame(columns=["Estado", "Fecha", "Texto Extraído", "Enlace"])
        
    return pd.DataFrame(data)
