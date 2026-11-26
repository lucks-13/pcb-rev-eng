import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

def find_kicad_cli(custom_cli : Optional[str] = None) -> str:
    if custom_cli:
        return custom_cli
    found = shutil.which("kicad-cli")
    if found:
        return found
    win_default = Path(r"C:\Program Files\KiCad\8.0\bin\kicad-cli.exe")
    if win_default.exists():
        return str(win_default)
    raise FileNotFoundError("")