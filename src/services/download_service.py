"""
Description:   Write a brief description of the script's purpose here.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import os
import requests


# Funcion para descrgar archivos dada una url y destino de descarga
def download_file(url, nombre_archivo, save_dir_path):
    """
    Descarga los archivos disponibles en la página especificada y los guarda en la ruta especificada.
    """

    # Asegurar que save_dir_path exista
    os.makedirs(save_dir_path, exist_ok=True)

    # Asegurar que save_dir_path sea absoluto y normalizar la ruta del archivo
    save_dir_path = (
        os.path.abspath(save_dir_path)
        if not os.path.isabs(save_dir_path)
        else save_dir_path
    )
    file_path = os.path.normpath(os.path.join(save_dir_path, nombre_archivo))

    # Realizar la solicitud HTTP para obtener el contenido de la página web
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    # Verifica si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Abre el archivo en modo binario y escribe los datos descargados
        with open(file_path, "wb") as f:
            f.write(response.content)

    else:
        raise FileNotFoundError("/n Error al descargar el archivo.")

    return file_path
