import json
from pathlib import Path
import cv2
from .schema import BroardDraft, ComponentItem, PinNode, NetEntry
from .exporters import export_draft

def render_debug_overlay(board_dir : Path, out_dir : Path) -> None:
    draft_path = out_dir / "draft_board.json"
    if not draft_path.exists():
        raise FileNotFoundError(f"Missing {draft_path}")
    with open(draft_path, )