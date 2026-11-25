import csv
import json
from pathlib import Path
from .schema import BroardDraft

def export_draft(draft : BroardDraft, out_dir : Path) -> None:
    out_dir.mkdir(parents = True, exist_ok = True)
    with open(out_dir / "draft_board.json", "w", encoding = "utf-8") as f:
        json.dump(draft.to_dict(), f, indent = 2)
    with open(out_dir / "bom.csv", "w", newline="", encoding = "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Designator", "PartType", "Value", "Footprint", "Confidence", "NeedsReview", "Notes"])
        for c in draft.components:
            