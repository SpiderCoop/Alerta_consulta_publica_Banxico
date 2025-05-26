# -*- coding: utf-8 -*-
"""
Created on Sun Nov  24 14:18:41 2024

@author: DJIMENEZ
"""
# Librerias necesarias ------------------------------------------------------------------------------------------
import os

import pandas as pd
import re

import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time

# Funcion auxiliar -------------------------------


def limpiar_caracteres(texto):
    """
    Elimina los acentos de un string utilizando expresiones regulares.
    """
    acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ü': 'u', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        '/':'_', ':':'_',
        '?':'', ',':''
    }

    # Reemplazar cada carácter acentuado por su equivalente sin acento
    patron = re.compile('|'.join(re.escape(k) for k in acentos.keys()))
    return patron.sub(lambda x: acentos[x.group()], texto)

# Funciones ------------------------------------------------------------------------------------------

def configurar_driver(directorio_descarga:str = None) -> webdriver.Chrome:
    """
    Configura el driver de Selenium con opciones para GitHub Actions y descargas en un directorio específico.

    Args:
        directorio_descarga (str): Ruta donde se guardarán los archivos descargados.

    Returns:
        webdriver.Chrome: Instancia del driver configurado.
    """
    # Crear el directorio de descarga si no existe
    if directorio_descarga and not os.path.exists(directorio_descarga):
        os.makedirs(directorio_descarga)

    # Configura opciones para Chrome
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": directorio_descarga, # Directorio para descargas
        "download.prompt_for_download": False,             # Evitar ventana de diálogo de descarga
        "download.directory_upgrade": True,                # Actualizar directorios automáticamente
        "safebrowsing.enabled": True                       # Habilitar navegación segura
    })

    # Configuraciones para entornos sin interfaz gráfica (headless)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Solucionar problemas de memoria compartida
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")  # Desactivar logs de DevTools
    chrome_options.add_argument("--start-maximized")

    # Iniciar el driver usando webdriver-manager para instalar ChromeDriver automáticamente
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver


# Funcion para revisar la pagina de consultas publicas de Banxico
def obtener_consultas_Banxico(driver, vigentes:bool=True):
    """
    Obtiene la lista de consultas públicas abiertas de la página de Banxico usando Selenium.
    """
    # Pagina de consultas publicas de Banxico
    url = "https://www.banxico.org.mx/ConsultaRegulacionWeb/"

    if vigentes:
        vigentes_txt = 'vigentes'
    else:
        vigentes_txt = 'historicas'

    # Navegar a la pagina especificada
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # Hace click en la lista de consultas vigentes
    try:   
        # Esperar a que cargue la tabla de consultas
        tabla_contenido = wait.until(EC.presence_of_element_located((By.ID, "tabs")))

        # Buscamos la tablist 
        ul_element = tabla_contenido.find_element(By.CSS_SELECTOR, 'ul[role="tablist"]')

        # Seleccionar el <li> con aria-controls="vigentes" y damos click
        li_vigentes = ul_element.find_element(By.CSS_SELECTOR, f'li[aria-controls="{vigentes_txt}"]')
        li_vigentes.click()

    except:
        print("Error al seleccionar la tab")
        driver.quit()

    try:
        # Esperar a que se cargue la tabla de contenido
        vigentes_div = wait.until(EC.presence_of_element_located((By.ID, vigentes_txt)))

        # Buscar todos los <li> dentro del <div> con class "rconrners"
        li_elements = vigentes_div.find_elements(By.CSS_SELECTOR, "li")
    
    except:
        driver.quit()
        raise ValueError("Error al buscar los elementos con la informacion de los proyectos de disposiciones")
        

    # Extraer información de los proyectos de disposiciones
    consultas = []
    for li in li_elements:

        # Nombre del proyecto
        try:
            nombre_proyecto = li.text.split("\n")[0]  # Primera línea es el nombre del proyecto
        except NoSuchElementException:
            nombre_proyecto = None

        # Fecha límite
        try:
            fecha_limite = li.find_element(By.CSS_SELECTOR, "span").text.strip()
        except NoSuchElementException:
            fecha_limite = None

        # Enlaces de descarga
        try:
            enlaces = li.find_elements(By.CSS_SELECTOR, "a.button")
            enlaces_descarga = {enlace.text.strip(): enlace.get_attribute("href") for enlace in enlaces}
        except NoSuchElementException:
            enlaces_descarga = {}

        # Agregar a la lista de consultas
        if nombre_proyecto and fecha_limite and enlaces_descarga:
            consultas.append({
                "nombre": nombre_proyecto,
                "fecha_limite": fecha_limite,
                "enlaces": enlaces_descarga
            })
    
    # Una vez terimando el proceso, cierra el navegador
    driver.quit()
    
    return pd.DataFrame(consultas)



# Funcion para descrgar archivos dada una url y destino de descarga
def descargar_archivo(url, nombre_archivo, save_path):
    """
    Descarga los archivos disponibles en una consulta específica utilizando requests.
    """

    file_path = os.path.join(save_path, limpiar_caracteres(nombre_archivo))
    file_path = os.path.normpath(file_path[:160] + '.pdf')

    # Realizar la solicitud HTTP para obtener el contenido de la página web
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    # Verifica si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Abre el archivo en modo binario y escribe los datos descargados
        with open(file_path, 'wb') as f:
            f.write(response.content)

    else:
        raise FileNotFoundError("/n Error al descargar el archivo.")
    
    return file_path

