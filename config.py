from pathlib import Path

BASE_DIR = Path(__file__).parent

INPUT = BASE_DIR / "input"
OUTPUT = BASE_DIR / "output"
REPORTS = INPUT / "reports"

TEMPLATES = BASE_DIR / "templates"
TEMPLATE = TEMPLATES / "template_frax.docx"