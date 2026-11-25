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

def find_cand_vias()