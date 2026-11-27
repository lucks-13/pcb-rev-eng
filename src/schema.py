from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict

@dataclass
class PinNode:
    pin_id : str
    designator : str
    pin_num : str
    side : str
    xy : 

@dataclass
class ComponentItem:
    

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
