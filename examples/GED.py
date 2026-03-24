import networkx as nx
import sys
PROXIMITY_NUM = {
    "near_coll": 0.16,
    "super_near": 0.28,
    "very_near": 0.4,
    "near": 0.64,
    "visible":1
}

def grid_to_scenegraph(grid):

    SG = nx.MultiDiGraph()

    SG.add_node("ego", type="ego")

    for cell, actors in grid.items():

        for actor in actors:

            name = actor["actor"]
            directions = actor["direction"]
            proximity = actor["proximity"]
            
            print(proximity)
            sys.exit()
            SG.add_node(name, type="car")

            if proximity:
                prox_label = proximity[0]

                SG.add_edge(
                    name,
                    "ego",
                    label=prox_label,
                    value=PROXIMITY_NUM.get(prox_label)
                )

            for rel in directions:

                SG.add_edge(
                    name,
                    "ego",
                    label=rel,
                    value=None
                )

    return SG

def print_scenegraph(G):

    print("\nNodes:")
    print(G.nodes(data=True))

    print("\nEdges:")
    for u, v, data in G.edges(data=True):
        print(u, "->", v, data)


import networkx as nx
import math

PROX_LABELS = [
    "near_coll",
    "super_near",
    "very_near",
    "near",
    "visible"
]

FRONT_REL = [
    "inSFrontOf",
    "atSRearOf"
]

SIDE_REL = [
    "toLeftOf",
    "toRightOf"
]


# -----------------------------------
# angle mapping (9-grid)
# -----------------------------------

ANGLE_MAP = {

    ("inSFrontOf", None): 0,
    ("inSFrontOf", "toRightOf"): 45,
    ("inSFrontOf", "toLeftOf"): 315,

    ("atSRearOf", None): 180,
    ("atSRearOf", "toRightOf"): 135,
    ("atSRearOf", "toLeftOf"): 225
}


# -----------------------------------
# extract actor relations
# -----------------------------------

def extract_actor_relations(G):

    relations = {}
    # print(G.edges())
    for u, v, data in G.edges( data=True):

        label = data.get("label")
        value = data.get("value")

        # print(label)
        # print(value)
        # detect ego-car relation
        if str(u).startswith("ego") and str(v).startswith("car"):
            car = v

        elif str(v).startswith("ego") and str(u).startswith("car"):
            car = u

        else:
            continue

        if car not in relations:
            relations[car] = {
                "proximity": None,
                "front": None,
                "side": None
            }

        if label in PROX_LABELS:
            relations[car]["proximity"] = value

        if label in FRONT_REL:
            relations[car]["front"] = label

        if label in SIDE_REL:
            relations[car]["side"] = label

    return relations


# -----------------------------------
# compute angle
# -----------------------------------

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
# proximity cost
# -----------------------------------

def proximity_cost(d1, d2, alpha=1):

    if d1 is None and d2 is None:
        return 0

    if d1 is None:
        return alpha * math.exp(-d2)

    if d2 is None:
        return alpha * math.exp(-d1)

    return alpha * abs(math.exp(-d1) - math.exp(-d2))


# -----------------------------------
# position cost
# modified formula
# -----------------------------------

def position_cost(theta1, theta2, d1, d2, beta=1):

    if theta1 is None or theta2 is None:
        return 0

    diff = math.radians(theta1 - theta2)

    return beta * ((d1 + d2) / (d1 * d2)) * abs(math.sin(diff / 2))


# -----------------------------------
# compute scene graph GED
# -----------------------------------

def scene_graph_distance(G1, G2, alpha=1, beta=1):

    #print("Debugging")
    r1 = extract_actor_relations(G1)
    #print(r1)
    r2 = extract_actor_relations(G2)
    #print(r2)
    actors = set(r1.keys()) | set(r2.keys())

    total_cost = 0

    for a in actors:

        d1 = None
        d2 = None
        theta1 = None
        theta2 = None

        if a in r1:

            d1 = r1[a]["proximity"]
            theta1 = compute_angle(
                r1[a]["front"],
                r1[a]["side"]
            )

        if a in r2:

            d2 = r2[a]["proximity"]
            theta2 = compute_angle(
                r2[a]["front"],
                r2[a]["side"]
            )

        prox = proximity_cost(d1, d2, alpha)
        print("prox", prox)
        pos = position_cost(theta1, theta2, d1, d2, beta)
        print("pos", pos)
        total_cost += prox + pos

    return total_cost