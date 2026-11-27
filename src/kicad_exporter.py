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

def export_kicad_sch(draft : BroardDraft, out_dir : Path) -> Path:
    out_dir.mkdir(parents = True, exist_ok = True)
    sch_path = out_dir / f"{draft.board_name}.kicad_sch"
    net_lookup = build_net_lookup(draft)
    lines: List[str] = [
        "(kicad_sch",
        "  (version 20231120)",
        '  (generator "pcb_rev_eng_draft")',
        '  (generator_version "1.0")',
        f"  (uuid {uid()})",
        '  (paper "A3")',
        "  (lib_symbols",
        "  )"
    ]

    start_x, start_y = 35.0, 35.0
    step_x = 58.0
    cols = 4
    row_y = start_y
    row_max_h = 0.0
    for idx, comp in enumerate(draft.components):
        col = idx % cols
        if idx > 0 and col == 0:
            ro
        row = idx // cols
        cx = round(start_x + col * step_x, 2)
        cy = round(start_y + row * step_y, 2)
        w, h = 16.0, 12.0
        x1, y1 = round(cx - w / 2, 2), round(cy - h / 2, 2)
        x2, y2 = round(cx + w / 2, 2), round(cy + h / 2, 2)
        lines.extend([
            "  (rectangle",
            f"  (start {x1} {y1})",
            f"  (end {x2} {y2})",
            "  (stroke (width 0.25) (type default))",
            "  (fill (type none))",
            f"  (uuid {uid()})",
            "  )",
            f'  (text "{esc(comp.designator)}" (at {cx} {round(y1 - 2.5, 2)} 0) (effects (font (size 1.5 1.5))))',
            f'  (text "{esc(comp.value)}" (at {cx} {round(y2 - 2.5, 2)} 0) (effects (font (size 1.27 1.27))))',
            f'  (text "FP : {esc(comp.footprint)}" (at {cx} {round(y2 - 5.0, 2)} 0) (effects (font (size 1.0 1.0)) (justify left)))',
        ])

        if comp.needs_review:
            lines.append(f'  (text "[REVIEW]" (at {cx} {round(y1 - 5.0, 2)} 0) (effects (font (size 1.27 1.27) (bold yes))))')
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