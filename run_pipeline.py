import argparse
from pathlib import Path
import cv2
import numpy as np
from src.schema import BroardDraft
from src.align import warp_board, align_btm_to_top
from src.vision import extract_trace_mark
from src.detector import PCBDetector
from src.graph_builder import build_netlist
from src.exporters import export_draft

def find_cand_vias(top_mask : np.ndarray, btm_mask : np.ndarray) -> list[tuple[int, int]]:
    overlap = cv2.bitwise_and(top_mask, btm_mask)
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(overlap)
    vias = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        if 12 <= area <= 400 and 0.6 <= (w / max(1, h)) <= 1.6:
            cx, cy = centroids[i]
            vias.append((int(cx), int(cy)))
    return vias

def main():
    parser = argparse.ArgumentParser(description = "Local 2-layer PCB image to draft BOM & netlist")
    parser.add_argument("--board", required = True, help = "Folder name under data/boards/")
    parser.add_argument("--weights", default = "", help = "Optional path to YOLO .pt weights")
    args = parser.parse_args()
    board_dir = Path("data/boards") / args.board
    out_dir = Path("outputs") / args.board
    out_dir.mkdir(parents = True, exist_ok = True)
    top_raw = cv2.imread(str(board_dir / "top.png"))
    btm_raw = cv2.imread(str(board_dir / "bottom.png"))
    if top_raw is None or btm_raw is None:
        raise FileNotFoundError(f"Expected top.png and bottom.png inside {board_dir}")
    th, tw = top_raw.shape[:2]
    bh, bw = btm_raw.shape[:2]
    top_align = warp_board(top_raw, [[0, 0], [tw - 1, 0], [tw - 1, th - 1], [0, th - 1]], out_size = (1600, 1200))
    btm_warp = warp_board(btm_raw, [[0, 0], [bw - 1, 0], [bw - 1, bh - 1], [0, bh - 1]], out_size = (1600, 1200))
    btm_align = align_btm_to_top(top_align, btm_warp)
    top_mask = extract_trace_mark(top_align)
    btm_mask = extract_trace_mark(btm_align)
    cv2.inwrite(str(out_dir / "top_aligned.png"), top_align)
    cv2.inwrite(str(out_dir / "bottom_aligned.png"), btm_align)
    cv2.inwrite(str(out_dir / "top_trace_mask.png"), top_mask)
    cv2.inwrite(str(out_dir / "bottom_trace_mask.png"), btm_mask)
    vias_xy = find_cand_vias(top_mask, btm_mask)
    detector = PCBDetector(parts_db_path = Path("data/parts_db.json"), yolo_weights = Path(args.weights) if args.weights else None, use_gpu = False)
    components, pins = detector.detect(top_align, btm_align,vias_xy)
    nets = build_netlist(top_mask, btm_mask, pins)
    draft = BroardDraft(board_name = args.board, img_size = (1600, 1200), components = components, pins = pins, nets = nets)
    expo
    
