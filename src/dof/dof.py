"""
Description:   Funcion integradora para el envio de las consultas publicas de Banxico
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import pandas as pd

from src.config import RECIPIENTS
from src.dof.email_body import create_email_body
from src.dof.web_scrapper import obtener_publicaciones_dof
from src.services.clean_text import clean_text
from src.services.email_manager import email
from src.services.log_service import LogService


def enviar_publicaciones_dof(date: pd.Timestamp | None = None):
    """
    Función principal para enviar publicaciones vigentes del DOF por correo electrónico.
    """

    date = pd.Timestamp.now() if date is None else date

    # Inicializamos el servicio de log para llevar un registro de los envios
    log_service = LogService()

    # Obtener las consultas vigentes
    publicaciones = obtener_publicaciones_dof(date=date)
    if not publicaciones.empty:
        # Iteramos sobre cada publicacion
        archivos_enviar = []
        for _index, row in publicaciones.iterrows():
            nombre_publicacion = clean_text(row["descripcion"])
            enlace = row["enlace"]
            nombre_registro = clean_text(
                nombre_publicacion + " - Fecha:" + date.strftime("%Y-%m-%d")
            )

            # Verificamos si ya se ha enviado un correo para esta consulta
            delivered = log_service.check_delivery(nombre_registro)

            # -------------------------------------------------------------------------------
            # Aqui tambien estaria la comprobacion de si la publicacion es relevante para la banca
            # -------------------------------------------------------------------------------

            # Si no se ha enviado, agregamos la publicacion a la lista de archivos a enviar
            if not delivered:
                archivos_enviar.append(
                    {"descripcion": nombre_publicacion, "enlace": enlace}
                )

        # Se envia el correo con los docuemntos adjuntos
        if archivos_enviar:
            asunto, cuerpo_correo = create_email_body(archivos_enviar, date=date)
            email.send(
                asunto,
                cuerpo_correo,
                RECIPIENTS.get("to"),
                RECIPIENTS.get("cc"),
                RECIPIENTS.get("bcc"),
            )

            # Una vez enviado, se guarda en el registro de envios para no volver a enviar el mismo archivo
            for archivo in archivos_enviar:
                nombre_registro = (
                    archivo["descripcion"] + " - Fecha:" + date.strftime("%Y-%m-%d")
                )
                log_service.log_delivery(nombre_registro)

    else:
        print("No hay publicaciones vigentes en el DOF en este momento.")
