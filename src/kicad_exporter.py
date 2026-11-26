import uuid
from pathlib import Path
from typing import Dict, List, Tuple
from .schema import BroardDraft, ComponentItem

def uid() -> str:
    return str(uuid.uuid4())

def esc(text : str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

def pin_count_for_comp(comp : ComponentItem, draft : BroardDraft) -> int:
    matching = [p for p in draft.pins if p.designator == comp.designator]
    return max(2, len(matching)) if matching else 2

def build_net_lookup(draft : BroardDraft) -> Dict[Tuple[str, str], str]:
    lookup : Dict[Tuple[str, str], str] = {}
    for net in draft.nets:
        for pin_ref in net.pins:
            if "." in p