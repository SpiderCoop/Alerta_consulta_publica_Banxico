# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 14:18:41 2023

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
#from webdriver_manager.chrome import ChromeDriverManager

import time

# Funciones de descarga ------------------------------------------------------------------------------------------

def configurar_driver(save_path:str):
    """
    Configura el driver de Selenium (utiliza Chrome en este caso).
    """
    # Configuracion inicial de Selenium 
    
    # Configura opciones para Chrome
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
    "download.default_directory": save_path,
    "download.prompt_for_download": False,  # Para evitar la ventana de diálogo de descarga
    "download.directory_upgrade": True,  # Para manejar directorios múltiples
    "safebrowsing.enabled": True  # Para evitar que Chrome bloquee descargas bajo consideración de 'peligrosas'
    })

    chrome_options.add_experimental_option("detach", True) # Mantiene el navegador abierto despues de que termina el script

    # Inicia el navegador con las opciones configuradas
    driver = webdriver.Chrome(options=chrome_options,keep_alive=True)

    return driver

def obtener_consultas(driver, vigentes:bool=True):
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
    proyectos = []
    for li in li_elements:
        # Nombre del proyecto
        nombre_proyecto = li.text.split("/n")[0]  # Primera línea es el nombre del proyecto

        # Fecha límite
        fecha_limite = li.find_element(By.CSS_SELECTOR, "span").text.strip()

        # Enlaces de descarga
        enlaces = li.find_elements(By.CSS_SELECTOR, "a.button")
        enlaces_descarga = {enlace.text.strip(): enlace.get_attribute("href") for enlace in enlaces}

        # Agregar a la lista de proyectos
        proyectos.append({
            "nombre": nombre_proyecto,
            "fecha_limite": fecha_limite,
            "enlaces": enlaces_descarga
        })

    # Una vez terimando el proceso, cierra el navegador
    driver.quit()
    
    return pd.DataFrame(proyectos)




def descargar_archivos(driver, consulta, carpeta_destino):
    """
    Descarga los archivos disponibles en una consulta específica utilizando Selenium.
    """
    driver.get(consulta['Enlace'])
    archivos_descargados = []
    
    # Esperar a que se carguen los enlaces de la consulta
    time.sleep(5)  # Agregar una espera fija para asegurar que la página se cargue completamente
    
    # Buscar enlaces a archivos
    enlaces = driver.find_elements(By.TAG_NAME, "a")
    for enlace in enlaces:
        href = enlace.get_attribute("href")
        if href and href.endswith(('.pdf', '.xlsx', '.csv', '.zip', '.docx')):
            nombre_archivo = href.split('/')[-1]
            archivo_path = os.path.join(carpeta_destino, nombre_archivo)
            
            # Descargar el archivo
            with open(archivo_path, 'wb') as f:
                f.write(requests.get(href).content)
            archivos_descargados.append(archivo_path)
    
    return archivos_descargados

def procesar_archivos(archivos):
    """
    Procesa los archivos descargados según el tipo de archivo.
    """
    datos = []
    for archivo in archivos:
        ext = os.path.splitext(archivo)[-1].lower()
        if ext == '.csv':
            datos.append(pd.read_csv(archivo))
        elif ext == '.xlsx':
            datos.append(pd.read_excel(archivo))
        # Puedes agregar más procesamientos específicos según el tipo de archivo
        else:
            print(f"Archivo {archivo} no procesado. Tipo no soportado.")
    return datos


if __name__ == "__main__":

    # Variables para prueba
    save_path = '/Consultas_publicas'

    # Configurar driver
    driver = configurar_driver(save_path)
    consultas = obtener_consultas(driver, False)
    consultas.to_csv('C:/ABM/Automatizacion/Alerta_consulta_publica_Banxico/Consultas_publicas/Consultas_historicas.csv', encoding='latin1')
