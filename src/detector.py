import re
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from .schema import ComponentItem, PinNode
from ultralytics import YOLO
from paddleocr import PaddleOCR

class PCBDetector:
    def __init__(self, parts_db_path : Path, yolo_weights : Optional[Path] = None, use_gpu : bool = False):
        with open(parts_db_path, "r", encoding = "utf-8") as f:
            self.parts_db : Dict = json.load(f)
        self.model = None
        if YOLO is not None and yolo_weights and yolo_weights.exists():
            self.model = YOLO(str(yolo_weights))
        self.ocr = None
        if PaddleOCR is not None:
            self.ocr = PaddleOCR(use_angle_cls = True, lang = "en", use_gpu = use_gpu, show_log = False)

    def run_ocr_crops(self, img : np.ndarray, boxes : List[Tuple[int, int, int, int]]) -> List[str]:
        if self.ocr is None:
            return ["" for _ in boxes]
        h, w = img.shape[:2]
        texts : List[str] = []
        pad = 24
        for (x1, y1, x2, y2) in boxes:
            cx1, cy1 = max