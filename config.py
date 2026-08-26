from pathlib import Path
import sys


def get_base_dir():
    """
    Devuelve la carpeta donde están los recursos de la aplicación.

    En desarrollo:
        carpeta donde está este archivo.

    En el .exe generado con PyInstaller:
        carpeta temporal donde PyInstaller extrae los recursos.
    """

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()

TEMPLATES = BASE_DIR / "templates"
TEMPLATE = TEMPLATES / "template_frax.docx"