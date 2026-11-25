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
        if p["side"] == "through"