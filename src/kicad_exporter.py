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

def build_symbol_instance(comp : ComponentItem, cx : float, cy : float, pin_count : int) -> List[str]:
    symbol_name = comp.symbol or "Device:R"
    return [
        f'  (symbol (lib_id "{esc(symbol_name)}") (at {cx} {cy} 0)',
        f'    (unit 1)',
        f'    (exclude_from_sim no)',
        f'    (in_bom yes)',
        f'    (on_board yes)',
        f'    (uuid {uid()})',
        f'    (property "Reference" "{esc(comp.designator)}" (at {cx} {cy - 7.62} 0)',
        '      (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{esc(comp.value)}" (at {cx} {cy + 7.62} 0)',
        '      (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{esc(comp.footprint)}" (at {cx} {cy} 0)',
        '      (effects (font (size 1.27 1.27)) hide))',
        '    (pin "1" (uuid ' + uid() + '))',
        '  )'
    ]

def expot_kicad_sch(draft : BroardDraft, out_dir : Path) -> Path:
    out_dir.mkdir(parents = True, exist_ok = True)
    sch_path = out_dir / f"{draft.board_name}.kicad_sch"
    net_lookup = build_net_lookup()
    lines : List[str] = [
        "(kicad_sch",
        "  (version 20231120)",
        '  (generator "pcb_rev_eng_draft")',
        '  (generator_version "1.0")',
        f"  (uuid {uid()})",
        '  (paper "A3")',
        "  (lib_symbols"
    ]
    for comp in draft.components:
        lines.extend(build_lib_symbol(comp, pin_count_for_comp(comp, draft)))
    lines.append("  )")
    start_