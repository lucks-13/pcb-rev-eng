import argparse
from pathlib import Path
from src.review_overlay import render_debug_overlay, re_export_from_edited_json

def main():
    parser = argparse.ArgumentParser(description = "Re-render overlays or re-export CSV from draft_board.json")
    parser