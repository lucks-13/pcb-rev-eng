import re
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from .schema import ComponentItem, PinNode
from ultralytics import YOLO
from paddleocr import PaddleOCR

class PCBDetector:
    def __init__(self, parts_db_pa):