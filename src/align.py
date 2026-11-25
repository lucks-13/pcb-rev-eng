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
    dst = np.array([[0,0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype = "float32")
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.wrapPerspective(img, M, (w, h))

def align_btm_to_top(top_img : np.ndarray, btm_img : np.ndarray) -> np.ndarray:
    flipped = cv2.flip(btm_img, 1)
    orb = cv2.
