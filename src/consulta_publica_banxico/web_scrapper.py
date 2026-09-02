"""
Description:   Web scrapping functions to extract information from the public consultation page of Banxico.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import pandas as pd
from driver_configuration import driver_configuration
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Funciones ------------------------------------------------------------------------------------------


# Funcion para revisar la pagina de consultas publicas de Banxico
def obtener_consultas_banxico(vigentes: bool = True):
    """
    Obtiene la lista de consultas públicas abiertas de la página de Banxico usando Selenium.
    """
    # Pagina de consultas publicas de Banxico
    url = "https://www.banxico.org.mx/ConsultaRegulacionWeb/"

    if vigentes:
        vigentes_txt = "vigentes"
    else:
        vigentes_txt = "historicas"

    # Navegar a la pagina especificada
    driver = driver_configuration()
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Hace click en la lista de consultas vigentes
    try:
        # Esperar a que cargue la tabla de consultas
        tabla_contenido = wait.until(EC.presence_of_element_located((By.ID, "tabs")))

        # Buscamos la tablist
        ul_element = tabla_contenido.find_element(By.CSS_SELECTOR, 'ul[role="tablist"]')

        # Seleccionar el <li> con aria-controls="vigentes" y damos click
        li_vigentes = ul_element.find_element(
            By.CSS_SELECTOR, f'li[aria-controls="{vigentes_txt}"]'
        )
        li_vigentes.click()

    except Exception as e:
        driver.quit()
        raise ValueError(f"Error al hacer click en la tab: {e}") from e

    try:
        # Esperar a que se cargue la tabla de contenido
        vigentes_div = wait.until(EC.presence_of_element_located((By.ID, vigentes_txt)))

        # Buscar todos los <li> dentro del <div> con class "rconrners"
        li_elements = vigentes_div.find_elements(By.CSS_SELECTOR, "li")

    except Exception as e:
        driver.quit()
        raise ValueError(
            f"Error al buscar los elementos con la informacion de los proyectos de disposiciones: {e}"
        ) from e

    # Extraer información de los proyectos de disposiciones
    consultas = []
    for li in li_elements:
        # Nombre del proyecto
        try:
            nombre_proyecto = li.text.split("\n")[
                0
            ]  # Primera línea es el nombre del proyecto
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
            enlaces_descarga = {
                enlace.text.strip(): enlace.get_attribute("href") for enlace in enlaces
            }
        except NoSuchElementException:
            enlaces_descarga = {}

        # Agregar a la lista de consultas
        if nombre_proyecto and fecha_limite and enlaces_descarga:
            consultas.append(
                {
                    "nombre": nombre_proyecto,
                    "fecha_limite": fecha_limite,
                    "enlaces": enlaces_descarga,
                }
            )

    # Una vez terimando el proceso, cierra el navegador
    driver.quit()

    return pd.DataFrame(consultas)
