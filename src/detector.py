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
            cx1, cy1 = max(0, x1 - pad), max(0, y1 - pad)
            cx2, cy2 = min(w, x2 + pad), min(h, y2 + pad)
            crop = img[cy1:cy2, cx1:cx2]
            if crop.size == 0:
                texts.append("")
                continue
            crop_up = cv2.resize(crop, None, fx = 2.0, fy = 2.0, interpolation = cv2.INTER_CUBIC)
            result  = self.ocr.ocr(crop_up, cls = True)
            found = []
            if result and result[0]:
                for line in result[0]:
                    txt, conf = line[1][0], line[1][1]
                    if conf >= 0.45 and txt.strip():
                        found.append(txt.strip())
            texts.append(" | ".join(found))
        return texts

    def infer_part_metadata(self, ocr_text : str, raw_cls : str) -> Tuple[str, str, str, float, bool, str]:
        upper = ocr_text.upper()
        
    
    