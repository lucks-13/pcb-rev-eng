import re
import json
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
from .schema import ComponentItem, PinNode
import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("YOLO_OFFLINE", "True")

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

try:
    from paddleocr import PaddleOCR
except Exception:
    PaddleOCR = None

class PCBDetector:
    def __init__(self, parts_db_path : Path, yolo_weights : Optional[Path] = None, use_gpu : bool = False):
        with open(parts_db_path, "r", encoding = "utf-8") as f:
            self.parts_db : Dict = json.load(f)
        self.model = None
        if YOLO is not None and yolo_weights and yolo_weights.exists():
            self.model = YOLO(str(yolo_weights))
        self.ocr = None
        if PaddleOCR is not None:
            for kw in (
                {
                    "lang": "en",
                    "enable_mkldnn": False,
                    "use_doc_orientation_classify": False,
                    "use_doc_unwarping": False,
                    "use_textline_orientation": False,
                },
                {"use_angle_cls": True, "lang": "en"},
                {"lang": "en"},
            ):
                try:
                    self.ocr = PaddleOCR(**kw)
                    break
                except TypeError:
                    continue
                except Exception:
                    self.ocr = None
                    break

    def run_ocr_crops(self, img : np.ndarray, boxes : List[Tuple[int, int, int, int]]) -> List[str]:
        if self.ocr is None:
            return ["" for _ in boxes]
        h, w = img.shape[:2]
        texts : List[str] = []
        pad = 28
        for (x1, y1, x2, y2) in boxes:
            cx1, cy1 = max(0, x1 - pad), max(0, y1 - pad)
            cx2, cy2 = min(w, x2 + pad), min(h, y2 + pad)
            crop = img[cy1:cy2, cx1:cx2]
            if crop.size == 0:
                texts.append("")
                continue
            crop_up = cv2.resize(crop, None, fx = 2.0, fy = 2.0, interpolation = cv2.INTER_CUBIC)
            found : List = []
            try:
                if hasattr(self.ocr, "predict"):
                    res = self.ocr.predict(crop_up)
                    if res:
                        for item in res:
                            text_list = item.get("rec_texts", []) if isinstance(item, dict) else getattr(item, "rec_texts", [])
                            scores_list = item.get("rec_scores", []) if isinstance(item, dict) else getattr(item, "rec_scores", [])
                            for txt, conf in zip(text_list, scores_list):
                                if float(conf) >= 0.45 and str(txt).strip():
                                    found.append(str(txt).strip())
                else:
                    result = self.ocr.ocr(crop_up, cls = True)
                    if result and result[0]:
                        for line in result[0]:
                            txt, conf = line[1][0], line[1][1]
                            if conf >= 0.45 and txt.strip():
                                found.append(txt.strip())
            except Exception:
                pass
            texts.append(" | ".join(found))
        return texts

    def infer_part_metadata(self, ocr_text : str, raw_cls : str) -> Tuple[str, str, str, str, float, bool, str]:
        upper = ocr_text.upper()
        des_match = re.search(r"\b([RCDULJQT]\d+)\b", upper)
        designator = des_match.group(1) if des_match else ""
        for part_key, info in self.parts_db.get("known_parts", {}).items():
            if re.search(rf"\b{re.escape(part_key.upper())}\b", upper) or part_key.upper() in upper:
                ptype = info.get("part_type", "ic")
                default_prefix = {"resistor" : "R", "capacitor" : "C", "ic" : "U", "diode" : "D", "inductor" : "L"}.get(ptype, "U")
                des = designator or f"{default_prefix}_{part_key.upper()}"
                return (des, ptype, info.get("default_value", part_key), info.get("footprint", "SOIC-8"), 0.90, False, f"Matched known part {part_key} from OCR : {ocr_text}")
        prefix = designator[0] if designator else ""
        type_map = {
            "R" : ("resistor", "0805", "R_UNK?"),
            "C" : ("capacitor", "0805", "C_UNK?"),
            "U" : ("ic", "SOIC-8", "IC_UNK?"),
            "D" : ("diode", "SOD-123", "D_UNK?"),
            "L" : ("inductor", "0805", "L_UNK?"),
            "J" : ("connector", "HDR-1X4", "CONN_UNK?"),
            "Q" : ("transistor", "SOT-23", "Q_UNK?"),
            "T" : ("transistor", "SOT-23", "T_UNK?")
        }
        if prefix in type_map:
            ptype, fp, val = type_map[prefix]
            needs_review = ptype in ("capacitor", "inductor", "ic", "transistor")
            notes = f"OCR : {ocr_text}" if ocr_text else "Designator inferred, verify value/footprint"
            return designator, ptype, val, fp, 0.75, needs_review, notes
        return ("", raw_cls or "unknown", "UNK?", "UNKNOWN", 0.40, True, f"Unclassified part, OCR : {ocr_text}" if ocr_text else "Unclassified part, no OCR text")

    def fallback_boxes(self, img: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blur, 40, 140)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates: List[Tuple[int, Tuple[int, int, int, int]]] = []
        min_area = max(100, int(0.0001 * w * h))
        max_area = int(0.08 * w * h)
        border = 4
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            x2, y2 = x + bw, y + bh
            if x <= border or y <= border or x2 >= w - border or y2 >= h - border:
                continue
            area = bw * bh
            if not (min_area <= area <= max_area):
                continue
            aspect = bw / max(1, bh)
            if not (0.15 <= aspect <= 7.0):
                continue
            candidates.append((area, (x, y, x2, y2)))
        candidates.sort(key=lambda item: item[0], reverse=True)
        selected: List[Tuple[int, int, int, int]] = []
        for _, box in candidates:
            if any(self.iou(box, prev) > 0.25 for prev in selected):
                continue
            selected.append(box)
            if len(selected) >= 30:
                break
        return [("candidate", box) for box in selected]

    @staticmethod
    def iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        if ix2 <= ix1 or iy2 <= iy1:
            return 0.0
        inter = (ix2 - ix1) * (iy2 - iy1)
        area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
        area_b = max(1, (bx2 - bx1) * (by2 - by1))
        return inter / float(area_a + area_b - inter)

    def gen_pins_for_component(self, comp: ComponentItem, side: str = "top") -> List[PinNode]:
        x1, y1, x2, y2 = comp.bbox
        fp_info = self.parts_db.get("footprints", {}).get(comp.footprint, {})
        pin_labels = fp_info.get("pins", ["1", "2"])
        n = len(pin_labels)
        pins: List[PinNode] = []
        mid_y = (y1 + y2) // 2
        if n == 2:
            pts = [(x1, mid_y), (x2, mid_y)]
        else:
            half = max(1, n // 2)
            pts = []
            for i in range(n):
                if i < half:
                    frac = (i + 0.5) / half
                    pts.append((x1, int(y1 + frac * (y2 - y1))))
                else:
                    frac = (i - half + 0.5) / max(1, n - half)
                    pts.append((x2, int(y1 + frac * (y2 - y1))))
        for label, xy in zip(pin_labels, pts):
            pins.append(PinNode(pin_id = f"{comp.designator}.{label}", designator = comp.designator, pin_num = str(label), side = side, xy = xy, confi = round(comp.confi * 0.85, 4)))
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
        else:
            for side_name, img in [("top", top_img), ("bottom", btm_img)]:
                for cls_name, bbox in self.fallback_boxes(img):
                    raw_detections.append((side_name, cls_name, bbox))
        components : List[ComponentItem] = []
        pins : List[PinNode] = []
        u_d : Set[str] = set()
        auto_idx = 1
        for side_name, cls_name, bbox in raw_detections:
            src_img = top_img if side_name == "top" else btm_img
            ocr_txt = self.run_ocr_crops(src_img, [bbox])[0]
            des, ptype, val, fp, conf, review, notes = self.infer_part_metadata(ocr_txt, cls_name)
            if not des:
                prefix = {"resistor" : "R", "capacitor" : "C", "ic" : "U", "diode" : "D", "inductor" : "L"}.get(ptype, "X")
                des = f"{prefix}_AUTO_{auto_idx}"
                auto_idx += 1
            if des in u_d:
                des = f"{des}_{side_name[0].upper()}{auto_idx}"
                auto_idx += 1
                review = True
                notes = f"{notes} | Disambiguated duplicate designator".strip(" |")
            u_d.add(des)
            comp = ComponentItem(designator = des, part_type = ptype, value = val, footprint = fp, bbox = bbox, confi = conf, needs_review = review, notes = notes)
            components.append(comp)
            pins.extend(self.gen_pins_for_component(comp, side = side_name))
        for idx, (vx, vy) in enumerate(vias_xy, start = 1):
            via_id  = f"VIA_{idx:03d}"
            pins.append(PinNode(pin_id = f"{via_id}.1", designator = via_id, pin_num = "1", side = "through", xy = (int(vx), int(vy)), confi = 0.75))
        return components, pins