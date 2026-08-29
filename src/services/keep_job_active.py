"""
Description:   Write a brief description of the script's purpose here.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-28
"""

import os
import random
from src.config import KEEP_JOB_ACTIVE_PATH


# Funcion para mantener el flujo habilitado creando diferencias en el repositorio y crear commits artificiales
def keep_job_active(save_path: str = KEEP_JOB_ACTIVE_PATH):

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    # Crea un archivo con un numero aleatorio
    number = random.random()
    number = (
        1 if number > 0.8 else 0
    )  # El valor cambia solo el 20% de las veces, lo suficiente para que se cree un commit cada cierto tiempo y mantener el flujo activo
    with open(save_path, "w") as archivo_logs:
        archivo_logs.write(f"{number}")
