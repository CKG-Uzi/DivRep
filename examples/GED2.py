import networkx as nx
import math
import config
import sys

# -----------------------------------
# proximity mapping
# -----------------------------------

PROXIMITY_NUM = {
    "near_coll": 0.16,
    "super_near": 0.28,
    "very_near": 0.4,
    "near": 0.64,
    "visible": 1
}

PROX_LABELS = list(PROXIMITY_NUM.keys())

FRONT_REL = ["inSFrontOf", "atSRearOf"]
SIDE_REL = ["toLeftOf", "toRightOf"]

# -----------------------------------
# angle mapping
# -----------------------------------

ANGLE_MAP = {
    ("inSFrontOf", None): 0,
    ("inSFrontOf", "toRightOf"): 45,
    ("inSFrontOf", "toLeftOf"): 315,

    ("atSRearOf", None): 180,
    ("atSRearOf", "toRightOf"): 135,
    ("atSRearOf", "toLeftOf"): 225
}


def compute_angle(front, side):

    key = (front, side)

    if key in ANGLE_MAP:
        return ANGLE_MAP[key]

    if front == "inSFrontOf":
        return 0

    if front == "atSRearOf":
        return 180

    return None


# -----------------------------------
# grid → scene graph
# -----------------------------------

def grid_to_scenegraph(grid):

    SG = nx.Graph()

    # ego
    SG.add_node("ego", id="ego", type="ego")

    for cell, actors in grid.items():

        for actor in actors:

            name = actor["actor"]
            directions = actor["direction"]
            proximity = actor["proximity"]
            print(proximity)
            # sys.exit()
            # proximity
            
            if proximity:
                prox_val = proximity[0]/10
            else:
                prox_val = 10000
            # extract relations
            front = None
            side = None

            for rel in directions:
                if rel in FRONT_REL:
                    front = rel
                if rel in SIDE_REL:
                    side = rel

            theta = compute_angle(front, side)

            SG.add_node(
                name,
                id=name,
                type="car",
                proximity=prox_val,
                angle=theta
            )

    return SG


# -----------------------------------
# cost functions
# -----------------------------------

def proximity_cost(d1, d2, alpha):

    if d1 is None and d2 is None:
        return 0

    if d1 is None:
        return alpha * math.exp(-d2)

    if d2 is None:
        return alpha * math.exp(-d1)

    return alpha * abs(math.exp(-d1) - math.exp(-d2))


def position_cost(theta1, theta2, d1, d2, beta):

    if theta1 is None or theta2 is None:
        return 0

    if d1 is None or d2 is None:
        return 0

    diff = math.radians(theta1 - theta2)

    return beta * ((d1 + d2) / (d1 * d2)) * abs(math.sin(diff / 2))



def node_subst_cost(n1, n2):

    # --- 强制 ID 对齐 ---
    if n1.get("id") != n2.get("id"):
        return float("inf")   # ❗ 禁止错误匹配

    # ego 不参与 cost
    if n1.get("type") == "ego":
        return 0

    d1 = n1.get("proximity")
    d2 = n2.get("proximity")

    theta1 = n1.get("angle")
    theta2 = n2.get("angle")
    alpha = config.ALPHA
    beta = config.BETA
    print("D", d1, d2)
    prox = proximity_cost(d1, d2, alpha)
    pos = position_cost(theta1, theta2, d1, d2, beta)

    return prox + pos

def node_del_cost(n):
    d = n.get("proximity")
    if d is None:
        return 0
    return config.ALPHA * math.exp(-d)


def node_ins_cost(n):
    d = n.get("proximity")
    if d is None:
        return 0
    return config.ALPHA * math.exp(-d)

# -----------------------------------
# GED computation
# -----------------------------------

def compute_ged(G1, G2):

    ged = nx.graph_edit_distance(
        G1,
        G2,
        node_subst_cost=node_subst_cost,
        node_del_cost=node_del_cost,
        node_ins_cost=node_ins_cost,
        edge_subst_cost=lambda e1, e2: 0,
        edge_del_cost=lambda e: 0,
        edge_ins_cost=lambda e: 0,
    )

    # ⚠️ 兼容 generator 返回
    if hasattr(ged, "__iter__"):
        ged = next(ged)

    return ged


# -----------------------------------
# debug
# -----------------------------------

def print_scenegraph(G):

    print("\nNodes:")
    for n, d in G.nodes(data=True):
        print(n, d)


# -----------------------------------
# example
# -----------------------------------

if __name__ == "__main__":

    grid1 = {
        "front": [
            {
                "actor": "car_1",
                "direction": ["inSFrontOf", "toLeftOf"],
                "proximity": ["near"]
            }
        ]
    }

    grid2 = {
        "front": [
            {
                "actor": "car_1",
                "direction": ["inSFrontOf"],
                "proximity": ["very_near"]
            }
        ]
    }

    G1 = grid_to_scenegraph(grid1)
    G2 = grid_to_scenegraph(grid2)

    print_scenegraph(G1)
    print_scenegraph(G2)

    ged = compute_ged(G1, G2)

    print("\nGraph Edit Distance:", ged)