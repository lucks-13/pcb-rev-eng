import re
import json
import cv2
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

    def infer_part_metadata(self, ocr_text : str, raw_cls : str) -> Tuple[str, str, str, str, float, bool, str]:
        upper = ocr_text.upper()
        for part_key, info in self.parts_db.get("known_parts", {}).items():
            if part_key.upper() in upper:
                des_match = re.search(r"\bU\d+\b", upper)
                des = des_match.group(0) if des_match else f"U_{part_key}"
                return (des, info.get("part_type", "ic"), info.get("default_value", part_key), info.get("footprint", "SOIC-8"), 0.85, False, f"Matched known part {part_key} from OCR : {ocr_text}")
        des_match = re.search(r"\b([RCDULJQT]\d+)\b", upper)
        designator = des_match.group(1) if des_match else ""
        prefix = designator[0] if designator else ""
        type_map = {
            "R" : ("resistor", "0805", "R_UNK?"),
            "C" : ("capacitor", "0805", "C_UNK?"),
            "U" : ("ic", "SOIC-8", "IC_UNK?"),
            "D" : ("diode", "SOD-123", "D_UNK?"),
            "L" : ("inductor", "0805", "L_UNK?"),
            "J" : ("connector", "HDR-1X4", "CONN_UNK?")
        }
        if prefix in type_map:
            ptype, fp, val = type_map[prefix]
            needs_review = ptype in ("capacitor", "inductor", "ic")
            notes = f"OCR : {ocr_text}" if ocr_text else "No OCR text; verify value/footprint"
            return designator, ptype, val,fp, 0.70, needs_review, notes
        return ("", raw_cls or "unknown", "UNK?", "UNKNOWN", 0.40, True, f"Unclassified part; OCR : {ocr_text}" if ocr_text else "Unclassified part; no OCR text")
    
    def gen_pins_for_component(self, comp : ComponentItem, side : str = "top") -> List[PinNode]:
        x1, y1, x2, y2 = comp.bbox
        fp_info = self.parts_db.get("footprints", {}).get(comp.footprint)
        pin_labels = fp_info["pins"] if fp_info else ["1", "2"]
        n =len(pin_labels)
        pins : List[PinNode] = []
        if n == 2:
            pts = [(x1 + int(0.25 * (x2 - x1)), (y1 + y2) // 2),(x2 - int(0.15 * (x2 - x1)), (y1 + y2) // 2)]
        else:
            half = max(1, n // 2)
            pts = []
            for i in range(n):
                if i < half:
                    frac = (i + 0.5) / half
                    pts.append((x1 + int(0.1 * (x2 - x1)), int(y1 + frac * (y2 - y1))))
                else:
                    frac = (i - half + 0.5) / max(1, n - half)
                    pts.append((x2 - int(0.1 * (x2 - x1)), int(y1 + frac * (y2 - y1))))
        for label, xy in zip(pin_labels, pts):
            pins.append(PinNode(pin_id = f"{comp.designator}.{label}", designator = comp.designator, pin_num = str(label), side = side, xy = xy, confi = comp.confi * 0.85))
        return pins

    def detect(self, top_img : np.ndarray, btm_img : np.ndarray, vias_xy : List[Tuple[int, int]]) -> Tuple[List[ComponentItem], List[PinNode]]:
        raw_detections : List[Tuple[str, str, Tuple[int, int, int,int]]] = []
        if self.model is not None:
            for side_name, img in [("top", top_img), ("bottom", btm_img)]:
                results = self.model.predict(img, verbose = False)
                for r in results:
                    names = r.names
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = names.get(cls_id, str(cls_id))
                        bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                        raw_detections.append((side_name, cls_name, (bx1, by1, bx2, by2)))
        components : List[ComponentItem] = []
        pins : List[PinNode] = []
        auto_idx = 1
        for side_name, cls_name, bbox in raw_detections:
            src_img = top_img if side_name == "top" else btm_img
            ocr_txt = self.run_ocr_crops(src_img, [bbox])[0]
            des, ptype, val, fp, conf, review, notes = self.infer_part_metadata(ocr_txt, cls_name)
            if not des:
                prefix = {"resistor" : "R", "capacitor" : "C", "ic" : "U", "diode" : "D", "inductor" : "L"}.get(ptype, "X")
                des = f"{prefix}_AUTO_{auto_idx}"
                auto_idx += 1
            comp = ComponentItem(designator = des, part_type = ptype, value = val, footprint = fp, bbox = bbox, confi = conf, needs_review = review, notes = notes)
            components.append(comp)
            pins.extend(self.gen_pins_for_component(comp, side = side_name))
        for idx, (vx, vy) in enumerate(vias_xy, start = 1):
            via_id  = f"VIA_{idx:03d}"
            pins.append(PinNode(pin_id = f"{via_id}.1", designator = via_id, pin_num = "1", side = "through", xy = (int(vx), int(vy)), confi = 0.75))
        return components, pins