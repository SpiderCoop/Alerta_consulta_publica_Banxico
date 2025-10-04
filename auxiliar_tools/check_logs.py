# -*- coding: utf-8 -*-
"""
Created on Mon May 26 10:14:41 2025

@author: DJIMENEZ
"""
# Librerias necesarias ------------------------------------------------------------------------------------------
import os
import random

# Funcion de verificacion de si la consulta ya se ha enviado o no
def revisar_registros_envio(nombre_consulta:str, save_path:str):
    
    # Carpeta donde se guardarán los archivos descargados
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    # Revisa en el logs de envios si ya se ha enviado o no
    if not os.path.exists(save_path):
        with open(save_path,'w') as archivo_logs:
            archivo_logs.write('Archivos enviados\n')
        nuevo = True
    else:
        with open(save_path,'r', encoding='latin-1') as archivo_logs:
            archivos_enviados = set(archivo_logs.read().splitlines())
    
        if nombre_consulta in archivos_enviados:
            nuevo = False
        else:
            nuevo = True
    
    return nuevo


# Funcion para mantener el flujo habilitado creando diferencias en el repositorio y crear commits artificiales
def mantener_flujo(save_path:str = os.path.normpath(os.path.join('Consultas_aux', 'mantener_flujo.txt'))):
    
    # Carpeta donde se guardarán los archivos descargados
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    # Crea un archivo con un numero aleatorio
    with open(save_path,'w') as archivo_logs:
        archivo_logs.write(f'{random.randint(0,1)}')

