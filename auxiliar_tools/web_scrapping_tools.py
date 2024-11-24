import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def configurar_driver():
    """
    Configura el driver de Selenium (utiliza Chrome en este caso).
    """
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def obtener_consultas_abiertas(driver, url):
    """
    Obtiene la lista de consultas públicas abiertas de la página de Banxico usando Selenium.
    """
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # Esperar a que cargue la tabla de consultas
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tablaContenido")))
    
    # Extraer filas de la tabla
    filas = driver.find_elements(By.CSS_SELECTOR, ".tablaContenido tr.filaTabla")
    consultas_abiertas = []
    
    for fila in filas:
        columnas = fila.find_elements(By.TAG_NAME, "td")
        if len(columnas) >= 3:  # Verificar que haya suficientes columnas
            nombre = columnas[0].text.strip()
            enlace = columnas[0].find_element(By.TAG_NAME, "a").get_attribute("href")
            estado = columnas[1].text.strip()
            fecha_cierre = columnas[2].text.strip()
            
            consultas_abiertas.append({
                'Nombre': nombre,
                'Enlace': enlace,
                'Estado': estado,
                'Fecha_Cierre': fecha_cierre
            })
    
    return pd.DataFrame(consultas_abiertas)

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


#if __name__ == "__main__":
    #main()
