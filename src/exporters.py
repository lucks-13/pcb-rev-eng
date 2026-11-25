import csv
import json
from pathlib import Path
from .schema import BroardDraft

def export_draft(draft : BroardDraft, out_dir : Path) -> None:
    out_dir.mkdir(parents = True, exist_ok = True)
    with open(out_dir / "draft_board.json", "w", en)