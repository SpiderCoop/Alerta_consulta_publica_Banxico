# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 20:15:30 2024

@author: DJIMENEZ
"""

# Librerias necesarias -------------------------------------------------------------------------

# Importa libreria para asignar el directorio de trabajo
import os

# Importa libreria para manejo de PDF
import fitz

# Importa libreria para manejo de imagenes
from PIL import Image

# Funciones para manejar archivos tipo PDF ----------------------------------------------------------------------------

# Verifica si el archivo pdf es valido
def verificar_pdf_valido(ruta_pdf):

    try:
        # Intenta abrir el archivo PDF
        documento = fitz.open(ruta_pdf)
        # Cierra el documento después de abrirlo
        documento.close()
        # Si no hay errores al abrir el documento, devuelve True
        return True
    except Exception as e:
        # Si hay algún error al abrir el documento, devuelve False
        return False

# Extrae texto de las paginas especificadas de un archivo PDF
def extract_text_from_pdf(ruta_pdf:str,num_pags:int|list):

    text = ''
    # Abrir el archivo PDF
    document = fitz.open(ruta_pdf)

    # Iterar sobre cada página del PDF
    if not isinstance(num_pags,list):
        num_pags = [num_pags]

    for page_number in num_pags:
        # Verifica el campo de numero de paginas
        if page_number<1:
            raise ValueError("El número de paginas debe ser un entero positivo")

        # Obtener el texto de la página actual y agregarlo al texto general
        page = document.load_page(page_number - 1)
        text += page.get_text()
    return text

# Convierte a imagen una parte del pdf
def pdf_to_image(pdf_path:str,save_path:str,pos_image:dict={'page_number':None,'coordinates':None}, resize_dims: tuple = None):
    # Verifica que los campos necesarios estén presentes en el diccionario
    if 'page_number' not in pos_image or 'coordinates' not in pos_image:
        raise ValueError("El diccionario 'pos_image' debe contener las llaves 'page_number' y 'coordinates'")
    
    # Trata de cambiar el tipo de valor a los corretos en caso de no serlo, si no puede lanza un error
    try:
        pos_image['page_number'] = int(pos_image['page_number'])
    except:
        raise ValueError("Error en 'pos_image': El valor de 'page_number' debe ser entero")
    
    try:
        pos_image['coordinates'] = tuple(pos_image['coordinates'])
    except:
        raise ValueError("Error en 'pos_image': El valor de 'coordinates' debe ser tupla")

    # Carpeta donde se guardarán los archivos descargados
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Abrir el archivo PDF
    document = fitz.open(pdf_path)
    # Seleccionar la página específica del PDF
    page = document.load_page(pos_image['page_number'] - 1)

    # Renderizar la página como una imagen con alta resolución (dpi más alto)
    zoom = 1.2  # Ajusta este valor según sea necesario para aumentar la resolución de la imagen
    mat = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix=mat)

    # Guardar la imagen en el disco
    # Obtener la extensión del archivo
    nombre_base, extension = os.path.splitext(pdf_path)
    image_path = os.path.normpath(os.path.join(save_path, nombre_base + '_imagen.png'))
    pixmap._writeIMG(image_path,'png',95)

    # Abre la imagen
    imagen = Image.open(image_path)
    
    # Recorta la imagen de acuerdo con las coordenadas de la región (x1, y1, x2, y2)
    imagen_recortada = imagen.crop(pos_image['coordinates'])

    # Si se proporciona resize_dims, cambiar el tamaño de la imagen recortada
    if resize_dims:
        try:
            imagen_recortada = imagen_recortada.resize(resize_dims, Image.LANCZOS)
        except:
            raise ValueError("Error en 'resize_dims': Los valores no son válidos")

    # Guarda la imagen recortada
    imagen_recortada.save(image_path)

    return os.path.abspath(image_path)











