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
    raise FileNotFoundError("Could not find kicad cli.")

def export_factory_package(board_name : str, out_dir : Path, kicad_cli_path : Optional[str] = None) -> Path:
    pcb_path = out_dir / f"{board_name}.kicad_pcb"
    if not pcb_path.exists():
        raise FileNotFoundError(f"Missing {pcb_path}.")
    cli = find_kicad_cli(kicad_cli_path)
    fab_dir = out_dir / "fab"
    if fab_dir.exists():
        shutil.rmtree(fab_dir)
    fab_dir.mkdir(parents = True, exist_ok = True)
    subprocess.run([cli, "pcb", "export", "gerbers", "--output", str(fab_dir) + "/", str(pcb_path)], check = True)
    subprocess.run([cli, "pcb", "export", "drill", "--output", str(fab_dir) + "/", str(pcb_path)], check = True)
    btm_src = out_dir / "bottom.csv"
    if btm_src.exists():
        shutil.copy2(btm_src, fab_dir / "bottom.csv")
    zip_path = out_dir / f"{board_name}_factory.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(fab_dir.rglob("*")):
            zf.write(file_path, arcname = file_path.relative_to(fab_dir))
    return zip_path
