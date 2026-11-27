from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict

@dataclass
class PinNode:
    pin_id : str
    designator : str
    pin_num : str
    side : str
    xy : Tuple[int, int]
    confi : float = 1.0
    source : str = "inferred"
    needs_review : bool = False
    notes : str = ""

@dataclass
class ComponentItem:
    designator : str
    part_type : str
    value : str
    footprint : str
    bbox : Tuple[int, int, int, int]
    confi : float
    notes : str = ""
    needs_review : bool = False
    symbol : str = ""

@dataclass
class NetEntry:
    net_name : str
    pins : List[str]
    confi : float
    flags : List[str] = field(default_factory=list)

@dataclass
class BroardDraft:
    board_name : str
    img_size : Tuple[int, int]
    components : List[ComponentItem]
    pins : List[PinNode]
    nets : List[NetEntry]
    def to_dict(self) -> Dict:
        return asdict(self)
