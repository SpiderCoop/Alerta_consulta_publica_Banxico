



# URL de la página de consultas públicas de Banxico
url = "https://www.banxico.org.mx/ConsultaRegulacionWeb/"

# Crear carpeta para guardar archivos descargados
carpeta_destino = "archivos_descargados"
if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Configurar Selenium WebDriver
driver = configurar_driver()

try:
    # Paso 1: Obtener la lista de consultas abiertas
    consultas = obtener_consultas_abiertas(driver, url)
    print("Consultas abiertas encontradas:")
    print(consultas)
    
    # Paso 2: Descargar los archivos de cada consulta
    for _, consulta in consultas.iterrows():
        print(f"Descargando archivos de la consulta: {consulta['Nombre']}")
        archivos_descargados = descargar_archivos(driver, consulta, carpeta_destino)
        print(f"Archivos descargados: {archivos_descargados}")
    
    # Paso 3: Procesar los archivos descargados
    print("Procesando archivos descargados...")
    archivos = [os.path.join(carpeta_destino, f) for f in os.listdir(carpeta_destino)]
    datos_procesados = procesar_archivos(archivos)
    
    # Mostrar los datos procesados
    for i, df in enumerate(datos_procesados):
        print(f"Datos procesados del archivo {archivos[i]}:")
        print(df.head())

finally:
    driver.quit()
