import uuid
from pathlib import Path
from typing import Dict, List, Tuple
from .schema import BroardDraft, ComponentItem

def uid() -> str:
    return str(uuid.uuid4())

def esc(text : str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

def pin_count_for_comp(comp : ComponentItem, draft : BroardDraft)