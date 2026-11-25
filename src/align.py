import cv2
import numpy as np

def ord_corners(pts : np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmin(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmin(diff)]
    return rect

def warp_board(img : np.ndarray, corners : np.ndarray, out_size = (1600, 1200)) -> np.ndarray:
    src = ord_corners(np.array(corners, dtype = "float32"))
    w, h = out_size
    dst = np.array([[]]) 
