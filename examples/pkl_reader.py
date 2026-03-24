import pickle
import os
import sys
from collections import defaultdict
import networkx as nx

sys.path.append(os.path.dirname(sys.path[0]))
from config import Tsim
from GED2 import grid_to_scenegraph, print_scenegraph, compute_ged
from roadscene2vec import util
from tools import find_lane_vehicles, find_vehicle_lane

sys.modules['util'] = util

with open("use_case_1_sg_extraction_output.pkl", "rb") as f:
    data = pickle.load(f)

print(type(data))
print(data.scene_graphs)

DIRECTION_REL = [
    "inDFrontOf",
    "inSFrontOf",
    "atDRearOf",
    "atSRearOf",
    "toLeftOf",
    "toRightOf"
]

PROX_REL = [
    "near",
    "visible",
    "super_near"
]


def determine_cell(direction):
    front = any(r in ["inDFrontOf", "inSFrontOf"] for r in direction)
    rear = any(r in ["atDRearOf", "atSRearOf"] for r in direction)

    left = "toLeftOf" in direction
    right = "toRightOf" in direction

    if front and left:
        return "front_left"
    if front and right:
        return "front_right"
    if front:
        return "front"
    if rear and left:
        return "rear_left"
    if rear and right:
        return "rear_right"
    if rear:
        return "rear"
    if left:
        return "left"
    if right:
        return "right"
    return "center"


def scenegraph_to_9grid(G):
    grid = {
        "front_left": [],
        "front": [],
        "front_right": [],
        "left": [],
        "center": [],
        "right": [],
        "rear_left": [],
        "rear": [],
        "rear_right": []
    }

    car_relations = defaultdict(list)

    for u, v, k, data in G.edges(keys=True, data=True):
        if str(u).startswith("car") and str(v).startswith("ego"):
            car = str(u)
            label = data.get("label")
            car_relations[car].append(label)

    print(car_relations)

    for car, relations in car_relations.items():
        direction = [r for r in relations if r in DIRECTION_REL]
        proximity = [r for r in relations if isinstance(r, float)]

        cell = determine_cell(direction)

        actor_data = {
            "actor": car,
            "direction": direction,
            "proximity": proximity
        }

        print(actor_data)
        grid[cell].append(actor_data)

    return grid


def print_grid(grid):
    print("\n===== 9 GRID =====\n")
    print(grid["front_left"], grid["front"], grid["front_right"])
    print(grid["left"], ["ego"], grid["right"])
    print(grid["rear_left"], grid["rear"], grid["rear_right"])
    print("\n==================\n")



# G = data.scene_graphs[22][7644].g

# # Print nodes
# print("Nodes:")
# for node, data in G.nodes(data=True):
#     print(node, data)

# # Print edges
# print("\nEdges:")
# for u, v, key, data in G.edges(keys=True, data=True):
#     print(f"{u} -> {v} (key={key})", data)
Failure_data = data.scene_graphs[22]
v = list(Failure_data.values())
print("V",v)

for x in range(len(v)-1, 1, -1):
    sc1 =  grid_to_scenegraph(scenegraph_to_9grid(v[x].g))
    sc2 =  grid_to_scenegraph(scenegraph_to_9grid(v[x-1].g))
    if compute_ged(sc1, sc2) < Tsim:
        print(x)
sys.exit()
grid = scenegraph_to_9grid(Failure_data[7646].g)
print("\n9-grid representation:\n", grid)
print_grid(grid)

SG = grid_to_scenegraph(grid)
print_scenegraph(SG)

grid2 = scenegraph_to_9grid(Failure_data[7647].g)
SG2 = grid_to_scenegraph(grid2)

print("\n9-grid representation:\n")
print_grid(grid2)

ged = compute_ged(SG, SG2)
print("Scene Graph GED:", ged)