import cv2
import numpy as np

def extract_trace_mark(aligned_bgr : np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(aligned_bgr, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, _ = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit = 2.5, tileGridSize = (8, 8))
    enhanced = clahe.apply(l_chan)
    mask = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN)
