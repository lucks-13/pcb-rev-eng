import cv2
import numpy as np

def extract_trace_mark(aligned_bgr : np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2LAB)
    l_chan, _, _ = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize = (8, 8))
    enhanced = clahe.apply(l_chan)
    mask = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, -4)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations = 1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations = 1)
    return mask
