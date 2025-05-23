# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 21:37:35 2024

@author: DJIMENEZ
"""

# Librerias necesarias -------------------------------------------------------------------------

import os

# Importa libreria para envio de correo
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

# Función para enviar correo alerta ----------------------------------------------------------------------------

# Configuración del servidor SMTP desde variables de entorno
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587

# Función para enviar correo electrónico
def enviar_correo(cuenta: str, password: str, destinatarios: list, asunto: str, cuerpo_correo: str, adjuntos: list = None):
    """
    Envía un correo electrónico con cuerpo HTML y adjuntos correctamente tipados.

    Args:
        cuenta (str): Correo del remitente.
        password (str): Contraseña del remitente.
        destinatarios (list): Lista de destinatarios.
        asunto (str): Asunto del correo.
        cuerpo_correo (str): Contenido HTML del mensaje.
        adjuntos (list): Lista de rutas de archivos a adjuntar.
    """
    # Crear mensaje base
    mensaje = MIMEMultipart()
    mensaje['From'] = cuenta
    mensaje['To'] = "; ".join(destinatarios)
    mensaje['Subject'] = asunto

    # Cuerpo HTML
    mensaje.attach(MIMEText(cuerpo_correo, 'html'))

    # Adjuntar archivos
    if adjuntos:
        for archivo in adjuntos:
            if not os.path.isfile(archivo):
                print(f"❌ Archivo no encontrado: {archivo}")
                continue

            ctype, encoding = mimetypes.guess_type(archivo)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)

            with open(archivo, 'rb') as f:
                mime_part = MIMEBase(maintype, subtype)
                mime_part.set_payload(f.read())

            encoders.encode_base64(mime_part)
            nombre_archivo = os.path.basename(archivo)
            mime_part.add_header('Content-Disposition', f'attachment; filename="{nombre_archivo}"')
            mensaje.attach(mime_part)

    # Enviar correo con conexión segura
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(cuenta, password)
            server.sendmail(cuenta, destinatarios, mensaje.as_string())
        print("✅ Correo enviado con éxito.")
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar correo: {e}")



# Funcion para crear el cuerpo del correo
def crear_cuerpo_correo(comentarios: list, fecha_str:str):
    
    # Se crea el cuerpo del correo de acuerdo con los puntos pasados como parámetro
    cuerpo = f'''
    <html>
    <head></head>
    <body style='font-family: Arial, sans-serif; font-size: 15px;'>
    <p><b>Hola, enviamos los indicadores oportunos con datos a {fecha_str} de CNBV. Saludos.</b></p>

    <p>Estimado, buenas tardes.</p>

    <p>Adjunto a este correo encontrarás el documento con los Indicadores Oportunos de la Cartera de Crédito con cifras a {fecha_str}, publicados recientemente por CNBV</p>

    <p>Principales resultados a {fecha_str}:</p>

    <ul style='font-style:italic;'>
    '''

    for punto in comentarios:
        if punto:
            cuerpo += f'<li>{punto}</li>'
    
    cuerpo += '''
    </ul>

    '''

    cuerpo += '''
    <p>Saludos</p>
    </body>
    </html>'''

    return cuerpo


