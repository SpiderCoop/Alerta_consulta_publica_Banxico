"""
Description:   Funcion integradora para el envio de las consultas publicas de Banxico
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import os

from src.config import RECIPIENTS, SAVE_DOWNLOAD_DIR_PATH
from src.consulta_publica_banxico.email_body import create_email_body
from src.consulta_publica_banxico.web_scrapper import obtener_consultas_banxico
from src.services.clean_text import clean_text
from src.services.download_service import download_file
from src.services.email_manager import email
from src.services.log_service import LogService


def enviar_consultas_banxico():
    """
    Función principal para enviar consultas vigentes de Banxico por correo electrónico.
    """

    # Inicializamos el servicio de log para llevar un registro de los envios
    log_service = LogService()

    # Obtener las consultas vigentes
    consultas = obtener_consultas_banxico(vigentes=True)
    if not consultas.empty:
        # Iteramos sobre cada registro de consulta
        for index, row in consultas.iterrows():
            nombre_consulta = row["nombre"]
            fecha_limite = row["fecha_limite"]
            nombre_consulta = clean_text(nombre_consulta + " - " + row["fecha_limite"])

            # Verificamos si ya se ha enviado un correo para esta consulta
            delivered = log_service.check_delivery(nombre_consulta)

            if not delivered:
                # Inicializamos una lista para guardar los nombres de los archivos descargados
                archivos_publicacion = []

                # Para cada consulta se revisan los documentos y si hay nuevos, se descargan
                for nombre_documento, enlace in row["enlaces"].items():
                    nombre_archivo = (
                        clean_text(nombre_documento) + " - " + nombre_consulta
                    )
                    nombre_archivo = nombre_archivo.replace("/", "_")[:150]
                    file_path = download_file(
                        enlace, nombre_archivo, SAVE_DOWNLOAD_DIR_PATH
                    )
                    archivos_publicacion.append(file_path)

                # Se envia el correo con los docuemntos adjuntos
                asunto, cuerpo_correo = create_email_body(nombre_consulta, fecha_limite)
                email.send(
                    asunto,
                    cuerpo_correo,
                    RECIPIENTS.get("to"),
                    RECIPIENTS.get("cc"),
                    RECIPIENTS.get("bcc"),
                    files=archivos_publicacion,
                )

                # Una vez enviado, se guarda en el registro de envios para no volver a enviar el mismo archivo
                log_service.log_delivery(nombre_consulta)

                # Una vez enviado el correo, se eliminan los archivos descargados
                for archivo in archivos_publicacion:
                    if os.path.exists(archivo):
                        os.remove(archivo)

    else:
        print("No hay consultas vigentes en Banxico en este momento.")
