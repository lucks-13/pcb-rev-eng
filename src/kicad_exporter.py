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
            
    lines.extend([
            "  (rectangle",
            f"  (start {x1} {y1})",
            f"  (end {x2} {y2})",
            "  (stroke (width 0.25) (type default))",
            "  (fill (type none))",
            f"  (uuid {uid()})",
            "  )",
            f'  (text "{esc(comp.designator)}" (at {cx} {round(y1 - 2.5, 2)} 0) (effects (font (size 1.5 1.5) (bold yes))))',
            f'  (text "{esc(comp.value)}" (at {cx} {round(y2 + 2.5, 2)} 0) (effects (font (size 1.27 1.27))))',
            f'  (text "FP: {esc(comp.footprint)}" (at {x1} {round(y2 + 5.2, 2)} 0) (effects (font (size 1.0 1.0)) (justify left)))',
        ])
        if comp.needs_review:
            lines.append(f'  (text "[REVIEW]" (at {cx} {round(y1 - 5.2, 2)} 0) (effects (font (size 1.27 1.27) (bold yes))))')
        comp_pins = [p for p in draft.pins if p.designator == comp.designator]
        if not comp_pins:
            comp_pins = []
        pin_count = max(1, len(comp_pins))
        for p_idx, p in enumerate(comp_pins):
            frac = (p_idx + 0.5) / pin_count
            py = round(y1 + frac * h, 2)
            left_side = p_idx < (pin_count / 2)
            px_body = x1 if left_side else x2
            px_end = round(px_body - 4.0, 2) if left_side else round(px_body + 4.0, 2)
            lines.extend([
                "  (wire",
                "  (pts",
                f"  (xy {px_body} {py})",
                f"  (xy {px_end} {py})",
                "  )",
                "  (stroke (width 0.15) (type default))",
                f"  (uuid {uid()})",
                "  )",
                f'  (text "{esc(p.pin_num)}" (at {round((px_body + px_end) / 2, 2)} {round(py - 1.2, 2)} 0) (effects (font (size 1.0 1.0))))'
            ])
            net_name = net_lookup.get((comp.designator, p.pin_num), "")
            if net_name:
                lines.append(f'  (label "{esc(net_name)}" (at {px_end} {py} 0) (effects (font (size 1.27 1.27)) (justify {"right" if left_side else "left"})))')
    lines.append(")")
    sch_path.write_text("\n".join(lines) + "\n", encoding = "utf-8")
    return sch_path