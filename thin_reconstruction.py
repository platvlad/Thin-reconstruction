#  PhotoScan project: P117_1804_MskHighway/P117_1804_MskHighway_2018_04_09_g201b20087_f001.psx

from thin_module.object_data import ObjectData
from thin_module.node import Node
from thin_module.mesh import Mesh
from collections import deque
import datetime
import numpy as np

file_path = "models/"

t0 = datetime.datetime.now().timestamp()
max_octree_height = 9
factor = 0
output_filename = factor == 0 and "strict" or factor > 0 and "votes"
output_filename += str(max_octree_height)

data = ObjectData()
box = data.bounding_box.bounds
cameras = data.cameras
req_votes_for_empty = 1
if len(cameras) > 2:
    req_votes_for_empty += factor * len(cameras)

t1 = datetime.datetime.now().timestamp()
ts = datetime.datetime.now().timestamp()
root_node = Node(None, 0, bounding_box=box)

processed_cubes = deque()
processed_cubes.append(root_node)
mesh = Mesh()
current_level = 0
cube_times = []
long_times = []

while len(processed_cubes) > 0:
    cube = processed_cubes.popleft()
    if cube.level > current_level:
        prev_ts = ts
        ts = datetime.datetime.now().timestamp()
        print(str(cube.level - 1), " level time: ", ts - prev_ts)
    current_level = cube.level
    for branch in range(8):
        start_cube = datetime.datetime.now().timestamp()
        node = Node(cube, branch, req_votes_for_empty)

        cube.children.append(node)
        before_camera = datetime.datetime.now().timestamp()
        for camera in cameras:
            time = None
            if int(node.status) > 1:
                time, status = node.project_on_camera(camera)
                if time is not None:
                    long_times.append(time)
        if int(node.status) == 2 and node.level < max_octree_height:
            processed_cubes.append(node)

        if int(node.status) == 3 or node.level == max_octree_height and int(node.status) == 2:
            mesh.add_cube(node.box)
        end_cube = datetime.datetime.now().timestamp()

        cube_times.append(end_cube - start_cube)

t3 = datetime.datetime.now().timestamp()
mesh.scale()

t4 = datetime.datetime.now().timestamp()
mesh.export(file_path + output_filename + ".obj")
tree_file = file_path + output_filename + ".txt"
tree_file = open(tree_file, "w")
root_node.print_tree('', file=tree_file)
tree_file.close()

print("bounding box counting time: ", t1 - t0)
print("last level time: ", t3 - ts)
print("writing file time: ", t4 - t3)
print("cube handling median: ", np.median(np.array(cube_times)))
print("cube variation: ", np.var(np.array(cube_times)))
print("max cube handling time: ", max(cube_times))
print("long_times: ")
print(long_times)

print("camera stats: ")
data.print_stats()
