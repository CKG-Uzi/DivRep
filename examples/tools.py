from collections import defaultdict

def find_lane_vehicles(edges):

    lane_vehicles = defaultdict(list)

    for src, dst, key, data in edges:

        if data.get("label") == "isIn":

            src_name = str(src)
            dst_name = str(dst)

            if src_name.startswith("car_") and dst_name.startswith("lane"):
                lane_vehicles[dst_name].append(src_name)

    return dict(lane_vehicles)
def find_vehicle_lane(vehicle_name, lane_dict):

    for lane, vehicles in lane_dict.items():
        if vehicle_name in vehicles:
            return lane

    return None
# # 示例 edges
# edges = [
# ('ego car', 'lane_middle', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1730', 'lane_right', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1782', 'lane_middle', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1547', 'lane_middle', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1583', 'lane_right', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1605', 'lane_middle', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1531', 'lane_middle', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1614', 'lane_right', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1678', 'lane_middle', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1706', 'lane_right', 0, {'value': 0, 'label': 'isIn'}),
# ('car_1710', 'lane_middle', 0, {'value': 0, 'label': 'isIn'})
# ]

# lane_dict = find_lane_vehicles(edges)

# for lane, vehicles in lane_dict.items():
#     print(f"{lane}: {vehicles}")