import cv2
import networkx as nx
from typing import List
from .schema import PinNode, NetEntry

def build_netlist(top_mask, btm_mask, pins : List[PinNode], snap_radius : int = 8) -> List[NetEntry]:
    G = nx.Graph()
    _, top_labels = cv2.connectedComponents(top_mask)
    _, btm_labels = cv2.connectedComponents(btm_mask)
    for p in pins:
        G.add_node(p.pin_id, meta = p)
        x, y = p.xy
        if p.side in ("top", "through"):
            lbl = sample_region(top_labels, x, y, )