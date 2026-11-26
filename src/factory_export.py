import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

def find_kicad_cli(custom_cli : Optional[str] = None) -> str:
    if custom_cli:
        return custom_cli
    found = shutil.which("kicad")