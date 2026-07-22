
# Librerias necesarias -------------------------------------------------------------------------

import os
from dotenv import load_dotenv
import json

# variables en secrets
load_dotenv()
cuenta = os.getenv('Cuenta')
password = os.getenv('password')
destinatarios = json.loads(os.getenv("Destinatarios"))
recipients = {
    'to': destinatarios.get('to', '').split(',') if isinstance(destinatarios.get('to', ''), str) else destinatarios.get('to', []),
    'cc': destinatarios.get('cc', '').split(',') if isinstance(destinatarios.get('cc', ''), str) else destinatarios.get('cc', []),
    'bcc': destinatarios.get('bcc', '').split(',') if isinstance(destinatarios.get('bcc', ''), str) else destinatarios.get('bcc', []),
    }

# Variable para guardar los registros de envios y descargas
save_download_path = "Consultas_publicas"
log_envios_path = "Consultas_aux/logs_envios.txt"
