# -*- coding: utf-8 -*-
"""
Created on Sun Nov  24 14:18:41 2024

@author: DJIMENEZ
"""

# Librerias necesarias -------------------------------------------------------------------------

import sys
import os

import pandas as pd

from dotenv import load_dotenv

from auxiliar_tools.web_scrapping_tools import configurar_driver, obtener_consultas_Banxico, descargar_archivo
from auxiliar_tools.check_logs import revisar_registros_envio, mantener_flujo
from auxiliar_tools.mail_tools import enviar_correo


# Configuracion iniacial -------------------------------------------------------------------------

# Obtener la ruta del directorio del archivo de script actual para establecer el directorio de trabajo
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
os.chdir(script_dir)

# Se toma la cuenta del archivo .env
load_dotenv()
cuenta = os.getenv('Cuenta')
password = os.getenv('password')
destinatarios = os.getenv("Destinatarios").split(',')

# Variable para guardar los registros de envios y descargas
save_logs_path = 'Consultas_aux'
save_download_path = 'Consultas_publicas'

log_envios_path = os.path.normpath(os.path.join(save_logs_path, 'logs_envios.txt'))

# Configurar driver
driver = configurar_driver()


# Flujo de trabajo -------------------------------------------------------------------------

mantener_flujo() # funcion auxiliar para mantener habilitado el flujo

# Obtener las consultas vigentes
consultas = obtener_consultas_Banxico(driver, vigentes=True)

# En caso de que existan consulta, se procesan los archivos
if not consultas.empty:

    # Iteramos sobre cada registro de consulta
    for index, row in consultas.iterrows():
        nombre_consulta = row['nombre']
        fecha_limite = row['fecha_limite']
        nombre_consulta = nombre_consulta + "-" + row['fecha_limite']
    
        # Inicializamos una lista para guardar los nombres de los archivos descargados
        nueva_publicacion = False
        archivos_publicacion = []

        # Para cada consulta se revisan los documentos y si hay nuevos, se descargan
        for nombre_documento, enlace in row['enlaces'].items():
            
            nombre_archivo = nombre_documento + ' - ' + nombre_consulta
            nuevo = revisar_registros_envio(nombre_consulta, log_envios_path)        
            if nuevo:
                file_path = descargar_archivo(enlace, nombre_archivo, save_download_path)
                archivos_publicacion.append(file_path)
                nueva_publicacion = True

        # Si hay una nueva publicacion se envia por correo
        if nueva_publicacion:

            # Se envian la notificacion de la nueva publicacion con los archivos descargados por correo
            asunto = f'Nueva Consulta Publica Banxico - {nombre_consulta}'
            cuerpo_correo = f"Se ha publicado una nueva consulta pública en la página de Banco de México con fecha límite al {fecha_limite} \n\n"

            # Se envia el correo con los docuemntos adjuntos
            enviar_correo(cuenta,password,destinatarios,asunto,cuerpo_correo, adjuntos=archivos_publicacion)

            # Una vez enviado, se guarda en el registro de envios para no volver a enviar el mismo archivo
            with open(log_envios_path,'a') as archivo_logs:
                archivo_logs.write(nombre_consulta + '\n')

            # Una vez enviado el correo, se eliminan los archivos descargados
            for archivo in archivos_publicacion:
                if os.path.exists(archivo):
                    os.remove(archivo)
            
        else:
            print(f"No hay nuevas publicaciones")

else:
    print("No hay consultas vigentes en Banxico en este momento.")