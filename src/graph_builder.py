import cv2
import networkx as nx
from typing import List
from .schema import PinNode, NetEntry

def build_netlist(top_mask, btm_mask, pins : List[PinNode], snap_radius : int = 8) -> List[NetEntry]:
    G = nx.Graph()
    _, top_labels = cv2.connected