from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict

@dataclass
class PinNode:
    pin_id : str
    designator : str
    pin_num : str
    side : str
    xy : Tuple[int, int]
    confi = float = 1.0

@dataclass
class ComponentItem:
    designator : str
    part_type : str
    value : str
    footprint : str
    bbox : 