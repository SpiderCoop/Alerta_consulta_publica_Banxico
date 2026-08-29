"""
Description:   Functions to clean and normalize text strings.
Author:        David Jiménez Cooper - SpiderCoop
Date:          2026-08-29
"""

import re


def clean_text(texto):
    """
    Elimina los acentos de un string utilizando expresiones regulares.
    """
    acentos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "ü": "u",
        "Ü": "U",
        "ñ": "n",
        "Ñ": "N",
        "/": "_",
        ":": "_",
        "?": "",
        ",": "",
    }

    # Reemplazar cada carácter acentuado por su equivalente sin acento
    patron = re.compile("|".join(re.escape(k) for k in acentos.keys()))
    return patron.sub(lambda x: acentos[x.group()], texto)
