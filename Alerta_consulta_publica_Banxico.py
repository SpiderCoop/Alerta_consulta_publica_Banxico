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

from auxiliar_tools.web_scrapping_tools import obtener_consultas_Banxico, configurar_driver, descargar_archivo, limpiar_caracteres
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

# Configurar driver
driver = configurar_driver()


# Flujo de trabajo -------------------------------------------------------------------------

# Obtener las consultas vigentes
consultas = obtener_consultas_Banxico(driver, vigentes=False)

# En caso de que existan consulta, se procesan los archivos
if not consultas.empty:
    for index, row in consultas.iterrows():
        nombre_consulta = row['nombre']
    
        # Inicializamos una lista para guardar los nombres de los archivos descargados
        archivos_descargados = []

        # Crear carpeta para guardar archivos descargados
        for nombre_documento, enlace in row['enlaces'].items():
            nombre_archivo = nombre_documento + ' - ' + nombre_consulta
            file_path = os.path.join(save_download_path, limpiar_caracteres(nombre_archivo))
            file_path = os.path.normpath(file_path[:50] + '.pdf')
            descargar_archivo(enlace, file_path)
            archivos_descargados.append(file_path)

        # Se envian los archivos descargados por correo
        # Se define el asunto y el cuerpo del correo
        asunto = f'Nueva Consulta Publica Banxico - {consultas["nombre"].values[0]}'
        cuerpo_correo = "Se han descargado los siguientes archivos de la consulta pública de Banxico:\n\n"

        # Se envia el correo con comentarios y el reporte adjunto
        enviar_correo(cuenta,password,destinatarios,asunto,cuerpo_correo, adjuntos=archivos_descargados)

        # Se guarda el log de envios
        log_envios_path = os.path.normpath(os.path.join(save_logs_path, 'logs_envios.txt'))
        with open(log_envios_path,'a') as archivo_logs:
            for archivo in archivos_descargados:
                archivo_logs.write(os.path.basename(archivo) + '\n')
