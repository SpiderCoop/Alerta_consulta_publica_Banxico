# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 20:15:30 2024

@author: DJIMENEZ
"""

# Librerias necesarias -------------------------------------------------------------------------
import win32com.client as win32
import os
import re
import shutil

# Funciones para buscar listas de distribucion y envio de correo ----------------------------------------------------------------------------

# Función para reiniciar el caché de Outlook en caso de error
def reset_outlook_cache():
    # Obtener el directorio del caché de win32com
    cache_dir = win32.gencache.GetGeneratePath()
    
    # Verificar si el directorio existe y eliminarlo si es así
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("Cache de win32com eliminado correctamente.")
    
    # Forzar la regeneración del caché
    win32.gencache.EnsureDispatch('Outlook.Application')
    print("Cache de win32com regenerado y conexión a Outlook restablecida.")

# Función para conectar con Outlook, reiniciando el caché si ocurre un error
def connect_outlook():
    try:
        outlook = win32.Dispatch("Outlook.Application")
        print("Conexión a Outlook establecida.")
        return outlook
    except AttributeError:
        print("Error de caché de win32com, limpiando caché y reintentando...")
        reset_outlook_cache()
        return win32.Dispatch("Outlook.Application")
    

# Funcion para buscar listas o contactos e la cuenta desaeada
def buscar_listas_distribucion(nombres_listas_dist:str | list,cuenta_deseada:str):

    if not isinstance(nombres_listas_dist,list):
        nombres_listas_dist = [nombres_listas_dist]

    outlook = connect_outlook()
    ns = outlook.GetNamespace("MAPI")
    accounts = ns.Accounts

    win32.constants 

    # Buscar la cuenta específica
    cuenta = None
    for i in range(accounts.Count):
        ac = accounts.Item(i + 1)
        if ac.DisplayName.lower() == cuenta_deseada.lower():
            cuenta = ac
            break

    # Verificar que se encontró la cuenta
    if cuenta is None:
        print(f"No se encontró la cuenta: {cuenta_deseada}")
        return []

    # Acceder al folder de contactos usando la cuenta especificada
    contacts_folder = ns.Folders[cuenta.DeliveryStore.DisplayName].Folders['Contactos']

    listas_distribucion = []
    for contact in contacts_folder.Items:
        if contact.Class == win32.constants.olDistributionList:
            # Verificar si el nombre de la lista de distribución está en la lista de nombres proporcionados
            if any(re.search(nombre_lista, contact.DLName, re.IGNORECASE) for nombre_lista in nombres_listas_dist):
                listas_distribucion.append(contact.DLName)
                
    return listas_distribucion

# Funcion para buscar las firmas guardadas
def obtener_firma_outlook(nombre_firma:str):
    # Determinar la ruta a la carpeta de firmas de Outlook
    user_profile = os.environ.get('USERPROFILE')
    firmas_base_path = os.path.normpath(os.path.join(user_profile, 'AppData', 'Roaming', 'Microsoft', 'Signatures'))

    # Leer el archivo HTML de la firma
    firma_html_path = os.path.normpath(os.path.join(firmas_base_path, f"{nombre_firma}.htm"))
    if os.path.exists(firma_html_path):
        try:
            with open(firma_html_path, 'r', encoding='utf-8') as file:
                firma_html = file.read()
        except UnicodeDecodeError:
            with open(firma_html_path, 'r', encoding='latin-1') as file:
                firma_html = file.read()
    else:
        print(f"No se encontró la firma: {firma_html_path}")
        firma_html = None

    # Obtener las imágenes referenciadas en la firma
    images = []
    img_pattern = re.compile(r'src=["\'](.*?)["\']', re.IGNORECASE)
    for img_src in img_pattern.findall(firma_html):
        img_path = os.path.normpath(os.path.join(firmas_base_path, img_src))
        img_path = img_path.replace('%20',' ')
        if os.path.exists(img_path):
            images.append(img_path)
            cid = os.path.basename(img_path)
            firma_html = firma_html.replace(img_src, f"cid:{cid}")

    # Se convierte en conjunto y se devuelve a lista para quitar duplicados
    images = list(set(images))

    return firma_html, images

# Funcion para la creacion de un correo de outlook
def enviar_correo(listas_dist:str | list, cuenta_deseada:str, asunto:str, cuerpo:str, nombre_firma:str=None, ruta_adjunto:str=None, ruta_imagen:str=None, imagen_inline:bool=True,send:bool=False):
    
    outlook = connect_outlook()
    ns = outlook.GetNamespace("MAPI")
    accounts = ns.Accounts

    # Buscar la cuenta específica
    cuenta = None
    for i in range(accounts.Count):
        ac = accounts.Item(i + 1)
        if ac.DisplayName.lower() == cuenta_deseada.lower():
            cuenta = ac
            break
    
    # Verificar que la cuenta ha sido encontrada
    if cuenta is None:
        print("\n")
        print(f"No se encontró la cuenta: {cuenta_deseada}")
        return False
    
    mail = outlook.CreateItem(0)
    mail._oleobj_.Invoke(*(64209, 0, 8, 0, cuenta))  # Enlaza el correo a la cuenta deseada

    # Usar la función buscar_listas_distribucion para obtener las listas
    listas_directo = listas_dist.get('directo')
    if listas_directo:
        listas_directo = buscar_listas_distribucion(listas_directo,cuenta_deseada)
        if listas_directo:
            mail.To = '; '.join(listas_directo)  # Unir todas las listas con ';'

    listas_copia = listas_dist.get('copia')
    if listas_copia:
        mail.CC = '; '.join(listas_copia)  # Unir todas las listas con ';'

    listas_copia_oculta = listas_dist.get('oculto')
    if listas_copia_oculta:
        listas_copia_oculta = buscar_listas_distribucion(listas_copia_oculta,cuenta_deseada)
        if listas_copia_oculta:
            mail.BCC = '; '.join(listas_copia_oculta)  # Unir todas las listas con ';'
    
    mail.Subject = asunto

    # Adjunta un archivo PDF
    if not ruta_adjunto==None:
        attachment_pdf = mail.Attachments.Add(ruta_adjunto)
    
    # Adjunta la imagen y marca como inline
    if not ruta_imagen==None:
        attachment = mail.Attachments.Add(ruta_imagen)
        if imagen_inline:
            attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "MiImagen")

    # Se incorpora la Firma si es definida
    if nombre_firma:
        firma_html, images = obtener_firma_outlook(nombre_firma)

        # Adjuntar las imágenes referenciadas en la firma
        for img_path in images:
            attachment = mail.Attachments.Add(img_path)
            cid = os.path.basename(img_path)
            attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", cid)
    else:
        firma_html = ""
    
    # Cuerpo del correo en HTML
    mail.HTMLBody = cuerpo + firma_html

    if send:
        mail.Send()
    else:
        mail.Display(True)
    
    print('\n El correo electrónico ha sido creado con éxito.')

    return True

# En caso de ser necesario se puede correr este script para reiniciar el cache de outlook
if __name__ == "__main__":
    reset_outlook_cache()
