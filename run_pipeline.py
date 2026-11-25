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
    parser = argparse.Parser(description = "Local 2-layer PCB image to draft BOM & netlist")
    
