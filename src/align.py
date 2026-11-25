import cv2
import numpy as np

def ord_corners(pts : np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2) )