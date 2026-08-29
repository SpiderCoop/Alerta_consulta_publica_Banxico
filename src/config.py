import os
from dotenv import load_dotenv
import json

load_dotenv()

CUENTA = os.getenv("Cuenta")
PASSWORD = os.getenv("password")
DESTINATARIOS = json.loads(os.getenv("Destinatarios", "{}"))
RECIPIENTS = {
    "to": DESTINATARIOS.get("to", "").split(",")
    if isinstance(DESTINATARIOS.get("to", ""), str)
    else DESTINATARIOS.get("to", []),
    "cc": DESTINATARIOS.get("cc", "").split(",")
    if isinstance(DESTINATARIOS.get("cc", ""), str)
    else DESTINATARIOS.get("cc", []),
    "bcc": DESTINATARIOS.get("bcc", "").split(",")
    if isinstance(DESTINATARIOS.get("bcc", ""), str)
    else DESTINATARIOS.get("bcc", []),
}

# Variable para guardar los registros de envios y descargas
SAVE_DOWNLOAD_DIR_PATH = "src/downloads"
LOG_DELIVERIES_PATH = "src/log_deliveries.db"
KEEP_JOB_ACTIVE_PATH = "src/keep_active.txt"
