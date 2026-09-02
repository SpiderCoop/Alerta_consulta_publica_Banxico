"""
Description:   Funciones para crear el cuerpo del correo electrónico para notificar sobre nuevas publicaciones en el DOF.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import pandas as pd


def create_email_body(archivos_enviar, date: pd.Timestamp | None = None):
    """
    Crea el cuerpo del correo electrónico para notificar sobre nuevas publicaciones en el Diario Oficial de la Federación.

    Args:
        archivos_enviar (list): Lista de diccionarios con 'descripcion' y 'enlace' de las publicaciones.
        date (pd.Timestamp): Fecha de las publicaciones.

    Returns:
        tuple: Asunto y cuerpo del correo electrónico.
    """

    date = pd.Timestamp.now() if date is None else date

    asunto = f"Nuevas Publicaciones en el DOF - {date.strftime('%Y-%m-%d')}"
    cuerpo_correo = """
    Se han publicado nuevas publicaciones en el Diario Oficial de la Federación.
    <br><br>
    """
    for archivo in archivos_enviar:
        nombre_publicacion = archivo["descripcion"]
        enlace = archivo["enlace"]
        cuerpo_correo += f'<b>{nombre_publicacion}</b><br><a href="{enlace}">Ver publicación</a><br><br>'
    cuerpo_correo += "<i>Este es un correo enviado de forma automatizada.</i>"

    return asunto, cuerpo_correo
