"""
Description:   Web scrapping functions to extract information from the public consultation page of Banxico.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import pandas as pd
from driver_configuration import driver_configuration
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Funciones ------------------------------------------------------------------------------------------


# Funcion para revisar la pagina de consultas publicas de Banxico
def obtener_publicaciones_dof(date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Obtiene la lista de consultas públicas abiertas de la página de Banxico usando Selenium.
    """

    # Si no se proporciona una fecha, se utiliza la fecha actual
    date = pd.Timestamp.now() if date is None else date

    # Construir la URL de la página de consultas públicas de Banxico para la fecha especificada
    url = f"https://dof.gob.mx/index_111.php?year={date.year}&month={date.month:02d}&day={date.day:02d}"

    # Navegar a la pagina especificada
    driver = driver_configuration()
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Hace click en la lista de consultas vigentes
    try:
        # Esperar a que cargue la pagina
        wait.until(EC.presence_of_element_located((By.ID, "cuerpo_principal")))

        # Buscar todos los elementos <a> con la clase "enlaces"
        elementos = driver.find_elements(By.CSS_SELECTOR, "a.enlaces")

        publicaciones = []
        for elem in elementos:
            descripcion = elem.text.strip()
            enlace = elem.get_attribute("href")  # Devuelve la URL absoluta
            publicaciones.append({"descripcion": descripcion, "enlace": enlace})

    except Exception as e:
        driver.quit()
        raise ValueError(f"Error al hacer click en la tab: {e}") from e

    finally:
        # Una vez terimando el proceso, cierra el navegador
        driver.quit()

        publicaciones_df = pd.DataFrame(publicaciones)

    return publicaciones_df
