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
        flag = " [REVIEW]" if c.get("needs_review") or c.get("confi", 1.0) < 0.70 else ""
        print(f"  - {c['designator']:<10} | type = {c['part_type']:<10} | val = {c['value']:<10} | fp = {c['footprint']:<8} | conf = {c['confi']:.2f}{flag}")
    flagged_nets = [n for n in nets if n.get("flags") or n.get("confi", 1.0) < 0.75]
    if flagged_nets:
        print("\nFlagged / Low confidence nets : ")
        for n in flagged_nets:
            print(f" - {n['net_name']:<8} | conf = {n['confi']:.2f} | flags = {','.join(n.get('flags', []))} | pins = {', '.join(n.get('pins', []))}")

def apply_tweak(out_dir : Path, designator : str, value : Optional[str] = None, footprint : Optional[str] = None, new_designator : Optional[str] = None, clear_review : bool = False, set_review : bool = False, pin_num : Optional[str] = None, pin_x : Optional[int] = None, pin_y : Optional[int] = None) -> bool:
    draft_path = out_dir / "draft_board.json"
    data = json.loads(draft_path.read_text(encoding = "utf-8"))
    target = next((c for c in data.get("components", []) if c["designator"] == designator), None)
    if target is None:
        print(f"Component '{designator}' not found in {draft_path}")
        return False
    if value is not None:
        target["value"] = value
    if footprint is not None:
        target["footprint"] = footprint
    if clear_review:
        target["needs_review"] = False
    elif set_review:
        target["needs_review"] = True
    if new_designator and new_designator != designator:
        old_des = target["designator"]
        target["designator"] = new_designator
        for p in data.get("pins", []):
            if p["designator"] == old_des:
                p["designator"] = new_designator
                p["pin_id"] = f"{new_designator}.{p['pin_num']}"
        for net in data.get("nets", []):
            net["pins"] = [f"{new_designator}.{pin_ref.split('.', 1)[1]}" if pin_ref.startswith(f"{old_des}.") else pin_ref for pin_ref in net.get("pins", [])]
    if pin_num is not None:
        for p in data.get("pins", []):
            if p["designator"] == designator and p["pin_num"] == pin_num:
                if pin_x is not None:
                    p["xy"][0] = pin_x
                if pin_y is not None:
                    p["xy"][1] = pin_y
                p["source"] = "manual"
                p["needs_review"] = False
    draft_path.write_text(json.dumps(data, indent = 2), encoding = "utf-8")
    return True

def main():
    parser = argparse.ArgumentParser(description = "Review draft, tweak low confidence parts and re-export")
    parser.add_argument("--board", required = True)
    parser.add_argument("--summary", action = "store_true", help = "Print component and flagged net summary")
    parser.add_argument("--part", default = "", help = "Designator to tweak (eg. X_AUTO_1 or R1)")
    parser.add_argument("--value", default = None, help = "New component value")
    parser.add_argument("--footprint", default = None, help = "New component footprint")
    parser.add_argument("--rename", default = None, help = "New designator (updates pins and nets)")
    parser.add_argument("--pin", default = None, help = "Pin number to move")
    parser.add_argument("--pin-x", type = int, default = None, help = "New pin X position")
    parser.add_argument("--pin-x", type = int, default = None, help = "New pin Y position")
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