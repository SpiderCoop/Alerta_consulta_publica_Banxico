"""
Description:   Write a brief description of the script's purpose here.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""


def create_email_body(nombre_consulta, fecha_limite):
    """
    Crea el cuerpo del correo electrónico para notificar sobre nuevas publicaciones en las consultas públicas del Banco de México.

    Args:
        nombre_consulta (str): Nombre de la consulta pública.
        fecha_limite (str): Fecha límite de la consulta pública.
        archivos_publicacion (list): Lista de nombres de archivos descargados.

    Returns:
        str: Cuerpo del correo electrónico.
    """

    asunto = f"Nueva Consulta Publica Banxico - {nombre_consulta}"
    cuerpo_correo = f"""
    Se ha publicado una nueva consulta pública en la página de Banco de México.
    <br><br><b>{fecha_limite}</b>
    <br><br><i>Este es un correo enviado de forma automatizada.</i>
    """

    return asunto, cuerpo_correo
