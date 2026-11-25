import argparse
from pathlib import Path
from src.review_overlay import render_debug_overlay, re_export_from_edited_json

def main():
    parser = argparse.ArgumentParser(description = "Re-render overlays or re-export CSV from draft_board.json")
    parser.add_argument("--board", required = True)
    parser.add_argument("--reexport", action = "store_true")
    args = parser.parse_args()

    board_dir = Path("data/boards") / args.board
    out_dir  = Path("outputs") / args.board

    if args.reexport:
        re_export_from_edited_json(out_dir)
        print(f"Re-exported bom.csv and netlist.csv in {out_dir}")

    render_debug_overlay(board_dir, )