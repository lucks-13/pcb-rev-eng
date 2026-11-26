import csv
import json
from pathlib import Path
from .schema import BroardDraft
from .kicad_exporter import export_kicad_sch

def export_draft(draft : BroardDraft, out_dir : Path) -> None:
    out_dir.mkdir(parents = True, exist_ok = True)
    with open(out_dir / "draft_board.json", "w", encoding = "utf-8") as f:
        json.dump(draft.to_dict(), f, indent = 2)
    with open(out_dir / "bottom.csv", "w", newline="", encoding = "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Designator", "PartType", "Value", "Footprint", "Confidence", "NeedsReview", "Notes"])
        for c in draft.components:
            writer.writerow([c.designator, c.part_type, c.value, c.footprint, c.confi, c.needs_review, c.notes])
    with open(out_dir / "netlist.csv", "w", newline="", encoding = "utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["NetName", "Designator", "Pin", "Confidence", "Flags"])
        for net in draft.nets:
            for pin_ref in net.pins:
                if "." in pin_ref:
                    des, pin = pin_ref.split(".", 1)
                    writer.writerow([net.net_name, des, pin, net.confi, ";".join(net.flags)])
    export_kicad_sch(draft, out_dir)

