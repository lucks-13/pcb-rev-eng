import argparse
import json
from pathlib import Path
from typing import Optional
from src.review_overlay import render_debug_overlay, re_export_from_edited_json

def print_review_summary(out_dir : Path) -> None:
    draft_path = out_dir / "draft_board.json"
    if not draft_path.exists():
        print(f"No draft_board.json found in {out_dir}")
        return
    data = json.loads(draft_path.read_text(encoding = "utf-8"))
    components = data.get("components", [])
    nets = data.get("nets", [])
    print(f"\nBoard Review : {data.get('board_name', out_dir.name)}")
    print(f"Components : {len(components)} | Nets : {len(nets)}")
    for c in components:
        flag = " [REVIEW]" if c.get("needs_review")

def main():
    parser = argparse.ArgumentParser(description = "Review draft, tweak low confidence parts and re-export")
    parser.add_argument("--board", required = True)
    parser.add_argument("--summary", action = "store_true", help = "Print component and flagged net summary")
    parser.add_argument("--part", default = "", help = "Designator to tweak (eg. X_AUTO_1 or R1)")
    parser.add_argument("--value", default = None, help = "New component value")
    parser.add_argument("--footprint", default = None, help = "New component footprint")
    parser.add_argument("--rename", default = None, help = "New designator (updates pins and nets)")
    parser.add_argument("--approve", action = "store_true", help = "Mark component as reviewed (needs_review = false)")
    parser.add_argument("--flag-review", action = "store_true", help = "Mark component as reviewed (needs_review = true)")
    parser.add_argument("--reexport", action = "store_true", help = "Re export .kicad_sch, bottom.csv and netlist.csv")
    parser.add_argument("--no-overlay", action = "store_true", help = "Skip re rendering overlay PNG")
    args = parser.parse_args()
    board_dir = Path("data/boards") / args.board
    out_dir  = Path("outputs") / args.board
    changed = False
    if args.part:
        changed = apply_tweak(out_dir = out_dir, designator = args.part, value = args.value, footprint = args.footprint, new_designator = args.rename, clear_review = args.approve, set_review = args.flag_review)
    if changed or args.reexport:
        re_export_from_edited_json(out_dir)
        print(f"Re exported .kicad_sch, bottom.csv and netlist.csv in {out_dir}")
    if not args.no_overlay and (changed or args.reexport or not args.summary):
        render_debug_overlay(board_dir, out_dir)
        print(f"Updated overlays in {out_dir}")    
    if args.summary or not (changed or args.reexport):
        print_review_summary(out_dir)
        
if __name__ == "__main__":
    main()