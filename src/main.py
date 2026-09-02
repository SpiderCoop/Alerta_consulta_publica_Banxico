"""
Description:   Funcion principal para enviar publicaciones.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

from src.consulta_publica_banxico.consulta_publica_banxico import (
    enviar_consultas_banxico,
)
from src.dof.dof import enviar_publicaciones_dof
from src.services.keep_job_active import keep_job_active

keep_job_active()  # funcion auxiliar para mantener habilitado el flujo
enviar_consultas_banxico()  # funcion principal para enviar consultas vigentes de Banxico por correo electrónico
enviar_publicaciones_dof()  # funcion principal para enviar publicaciones vigentes del DOF por correo electrónico
