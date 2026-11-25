import json
from pathlib import Path
import cv2
from .schema import BroardDraft, ComponentItem, PinNode, NetEntry
from .exporters import export_draft

def render_debug_overlay(board_dir : Path, out_dir : Path) -> None:
    draft_path = out_dir / "draft_board.json"
    if not draft_path.exists():
        raise FileNotFoundError(f"Missing {draft_path}")
    with open(draft_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
    top_vis = cv2.imread(str(out_dir / "top_aligned.png"))
    btm_vis = cv2.imread(str(out_dir / "bottom_aligned.png"))
    if top_vis is None or btm_vis is None:
        raise FileNotFoundError("Missing aligned images in output folder.")
    pin_sides = {p["pin_id"] : p["side"] for p in data.get("pins", [])}
    for p in data.get("pins", []):
        x, y = p["xy"]
        if p["side"] == "through":
            cv2.circle(top_vis, (x, y), 6, (0, 255, 255), 2)
            cv2.circle(btm_vis, (x, y), 6, (0, 255, 255), 2)
        elif p["side"] == "top":
            cv2.circle(top_vis, (x, y), 4, (255, 0, 255), -1)
        elif p["side"] == "bottom":
            cv2.circle(btm_vis, (x, y), 4, (255, 0, 255), -1)
    for c in data.get("components", []):
        x1, y1, x2, y2 = c["bbox"]
        color = (0, 165, 255) if c.get("needs_review") else (0, 255, 0)
        label = f"{c['designator']} ({c['value']})"
        prefix = f"{c['designator']}"
        sides = {s for pid, s in pin_sides.items() if pid.startswith(prefix)}
        target = btm_vis if sides == {"bottom"} else top_vis
        cv2.rectangle(target, (x1, y1), (x2, y2), color, 2)
        cv2.putText(target, label, (x1, max(15, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
    cv2.imwrite(str(out_dir / "top_overlay.png"), top_vis)
    cv2.imwrite(str(out_dir / "bottom_overlay.png"), btm_vis)

def re_export_from_edited_json(out_dir : Path) -> None:
    with open(out_dir / "draft_board.json", "r", encoding = "utf-8") as f:
        d = json.load(f)
    draft = BroardDraft(board_name = d["board_name"], img_size = tuple(d["img_size"]), components = [ComponentItem(**c) for c in d["components"]], pins = [PinNode(**p) for p in d["pins"]], nets = [NetEntry(**n) for n in d["nets"]])
    export_draft(draft, out_dir)