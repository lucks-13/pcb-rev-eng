import cv2
import networkx as nx
import numpy as np
from typing import List
from .schema import PinNode, NetEntry

def build_netlist(top_mask : np.ndarray, btm_mask : np.ndarray, pins : List[PinNode], snap_radius : int = 16, ray_reach : int = 24) -> List[NetEntry]:
    G = nx.Graph()
    _, top_labels = cv2.connectedComponents(top_mask)
    _, btm_labels = cv2.connectedComponents(btm_mask)
    for p in pins:
        G.add_node(p.pin_id, meta = p)
        x, y = p.xy
        if p.side in ("top", "through"):
            lbl = sample_region(top_labels, x, y, snap_radius, ray_reach)
            if lbl > 0:
                G.add_edge(p.pin_id, f"TOP_COPPER_{lbl}")
        if p.side in ("bottom", "through"):
            lbl = sample_region(btm_labels, x, y, snap_radius, ray_reach)
            if lbl > 0:
                G.add_edge(p.pin_id, f"BOTTOM_COPPER_{lbl}")
    nets : List[NetEntry] = []
    idx = 1
    for comp in nx.connected_components(G):
        pin_nodes = sorted([n for n in comp if not n.startswith(("TOP_COPPER_", "BOTTOM_COPPER_"))])
        if len(pin_nodes) < 2:
            continue
        copper_bridge = [n for n in comp if n.statswith(("TOP_COOPER_", "BOTTOM_COPPER_"))]
        flags : List[str] = []
        confi = 0.85
        if len(copper_bridge) > 2:
            flags.append("MULTI_COPPER_BRIDGE")
            confi = 0.65
        elif len(copper_bridge) == 0:
            flags.append("DIRECT")

        nets.append(NetEntry(net_name=f"NET_{idx:03d}", pins = pin_nodes, confi = 0.80, flags = []))
        idx += 1
    return nets

def sample_region(label_map, x : int, y : int, r : int) -> int:
    h, w = label_map.shape
    if x < 0 or y < 0 or x >= w or y >= h:
        return 0
    patch = label_map[max(0, y - r) : min(h, y + r + 1), max(0, x - r) : min(w, x + r + 1)]
    nonzero = patch[patch > 0]
    if len(nonzero) == 0:
        return 0
    vals, counts = np.unique(nonzero, return_counts = True)
    return int(vals[np.argmax(counts)])