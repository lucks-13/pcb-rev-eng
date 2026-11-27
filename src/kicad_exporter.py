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
            if "." in pin_ref:
                des, pin = pin_ref.split(".", 1)
                lookup[(des.strip(), pin.strip())] = net.net_name
    return lookup

def build_lib_symbol(comp : ComponentItem, pin_count : int) -> List[str]:
    symbol_name = comp.symbol or "Device:R"
    lines = [
        f'    (symbol "{esc(symbol_name)}"',
        f'      (pin_names (offset 0.7))',
        '      (exclude_from_sim no)',
        '      (in_bom yes)',
        '      (on_board yes)',
        '      (property "Reference" "U" (at 0 3.81 0)',
        '        (effects (font (size 1.27 1.27))))',
        f'      (property "Value" "{esc(comp.value)}" (at 0 1.27 0)',
        '        (effects (font (size 1.27 1.27))))',
        f'      (property "Footprint" "{esc(comp.footprint)}" (at 0 0 0)',
        '        (effects (font (size 1.27 1.27)) hide))',
        '      (symbol "body"',
        '        (rectangle',
        '          (start -5.08 -5.08)',
        '          (end 5.08 5.08)',
        '          (stroke (width 0) (type default))',
        '          (fill (type background))',
        f'          (uuid {uid()})',
        '        )',
        '      )'
    ]
    spacing = max(2.54, 10.16 / max(1, pin_count))
    half = max(1, pin_count // 2)
    for idx in range(pin_count):
        pin_num = str(idx + 1)
        if idx < half:
            y = round((idx - (half - 1) / 2) * spacing, 2)
            x = -7.62
            angle = 0
        else:
            right_idx = idx - half
            right_count = pin_count - half
            y = round((right_idx - (right_count - 1) / 2) * spacing, 2)
            x = 7.62
            angle = 180
        lines.extend([
            f'        (pin passive line (at {x} {y} {angle}) (length 2.54)',
            f'          (name "{pin_num}" (effects (font (size 1.27 1.27))))',
            f'          (number "{pin_num}" (effects (font (size 1.27 1.27))))',
            f'          (uuid {uid()})',
            '        )'
        ])
    lines.extend([
        '      )',
        '    )'
    ])
    return lines

def build_symbol_instance