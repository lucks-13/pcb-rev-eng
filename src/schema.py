from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Optional, Dict

@dataclass
class PinNode:
    pin_id : str
    designator : str
    pi