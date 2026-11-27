import cv2
import numpy as np

def ord_corners(pts : np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def warp_board(img : np.ndarray, corners : np.ndarray, out_size = (1600, 1200)) -> np.ndarray:
    src = ord_corners(np.array(corners, dtype = "float32"))
    w, h = out_size
    dst = np.array([[0,0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype = "float32")
    M = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, M, (w, h))

def valid_homogrphy(H : np.ndarray, w : int, h : int) -> bool:
    if H is None or H.shape != (3, 3) or not np.all(np.isfinite(H)):
        return False
    det = float(np.linalg.det(H[:2, :2]))
    if det < 0.25 or det > 4.0:
        return False
    corners = np.array([[0.0, 0.0], [float(w - 1), 0.0], [float(w - 1), float(h - 1)], [0.0, float(h - 1)]], dtype = "float32").reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform((corners, H).res)

def align_btm_to_top(top_img : np.ndarray, btm_img : np.ndarray) -> np.ndarray:
    flipped = cv2.flip(btm_img, 1)
    orb = cv2.ORB_create(3000)
    kp1, des1 = orb.detectAndCompute(top_img, None)
    kp2, des2 = orb.detectAndCompute(flipped, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
    matches = sorted(bf.match(des1, des2), key = lambda m : m.distance)[:200]
    src_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    h, w = top_img.shape[:2]
    return cv2.warpPerspective(flipped, H, (w, h))