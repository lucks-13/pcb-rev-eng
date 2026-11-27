import argparse
import json
from pathlib import Path
from typing import Optional
from src.review_overlay import render_debug_overlay, re_export_from_edited_json

def main():
    parser = argparse.ArgumentParser(description = "Review draft, tweak low confidence parts and re-export")
    parser.add_argument("--board", required = True)
    parser.add_argument("--summary", action = "store_true", help = "Print component and flagged net summary")
    parser.add_argument("--part", default = "", help = "Designator to tweak (eg. X_AUTO_1 or R1)")
    parser.add_argument("--value", default = None, help = "New component value")
    parser.add_argument("--footprint", default = None, help = "New component footprint")
    parser.add_argument("--rename", default = None, help = "New designator (updates pins and nets)")
    


    parser.add_argument("--reexport", action = "store_true")
    args = parser.parse_args()
    board_dir = Path("data/boards") / args.board
    out_dir  = Path("outputs") / args.board

    if args.reexport:
        re_export_from_edited_json(out_dir)
        print(f"Re-exported bottom.csv and netlist.csv in {out_dir}")

    render_debug_overlay(board_dir, out_dir)
    print(f"Updated overlays in {out_dir}")

if __name__ == "__main__":
    main()