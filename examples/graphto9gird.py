import networkx as nx
from collections import defaultdict


# -----------------------------
# 9-grid layout definition
# -----------------------------
GRID_CELLS = [
    "front_left", "front", "front_right",
    "left", "center", "right",
    "rear_left", "rear", "rear_right"
]


# -----------------------------
# relation categories
# -----------------------------
DIRECTION_REL = {
    "inDFrontOf", "inSFrontOf",
    "atDRearOf", "atSRearOf",
    "toLeftOf", "toRightOf"
}

PROX_REL = {
    "near_coll",
    "super_near",
    "very_near",
    "near",
    "visible"
}


# -----------------------------
# determine grid cell
# -----------------------------
def determine_cell(direction_relations):

    front = any(r in ["inDFrontOf", "inSFrontOf"] for r in direction_relations)
    rear = any(r in ["atDRearOf", "atSRearOf"] for r in direction_relations)

    left = "toLeftOf" in direction_relations
    right = "toRightOf" in direction_relations

    if front and left:
        return "front_left"

    if front and right:
        return "front_right"

    if rear and left:
        return "rear_left"

    if rear and right:
        return "rear_right"

    if front:
        return "front"

    if rear:
        return "rear"

    if left:
        return "left"

    if right:
        return "right"

    return "front"


# -----------------------------
# main conversion function
# -----------------------------
def convert_scenegraph_to_9grid(G, ego="ego car"):

    grid = {cell: [] for cell in GRID_CELLS}

    # ego occupies center
    grid["center"].append({
        "actor": ego
    })

    # iterate ego outgoing edges
    for u, v, k, data in G.edges(keys=True, data=True):

        if u != ego:
            continue

        if not str(v).startswith("car"):
            continue

        # collect all relations between ego and this actor
        relations = [
            d["label"]
            for _, _, _, d in G.edges(u, v, keys=True, data=True)
        ]

        direction = [r for r in relations if r in DIRECTION_REL]
        proximity = [r for r in relations if r in PROX_REL]

        cell = determine_cell(direction)

        actor_data = {
            "actor": v,
            "direction_relations": direction,
            "proximity_relations": proximity,
            "all_relations": relations
        }

        grid[cell].append(actor_data)

    return grid


# -----------------------------
# optional: pretty print
# -----------------------------
def print_grid(grid):

    order = [
        ["front_left", "front", "front_right"],
        ["left", "center", "right"],
        ["rear_left", "rear", "rear_right"]
    ]

    for row in order:
        for cell in row:
            actors = [a["actor"] if isinstance(a, dict) else a for a in grid[cell]]
            print(f"{cell:12} : {actors}")
        print()
