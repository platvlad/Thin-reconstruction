from enum import IntEnum
import datetime


class Status(IntEnum):
    Empty = 1
    Refine = 2
    Full = 3
    Final = 4


class Node:
    def __init__(self, parent, branch_num, bounding_box=None, req_votes_for_empty=1):  # specify bounding_box if parent is None
        if parent is None:
            self.level = 0
            self.box = bounding_box
        else:
            self.level = parent.level + 1
            x_is_big = (branch_num % 2 == 0)
            y_is_big = (branch_num % 4 > 1)
            z_is_big = (branch_num > 3)

            middle_x = (parent.box[0][0] + parent.box[1][0]) / 2.
            middle_y = (parent.box[0][1] + parent.box[1][1]) / 2.
            middle_z = (parent.box[0][2] + parent.box[1][2]) / 2.

            min_x = x_is_big and middle_x or not x_is_big and parent.box[0][0]
            min_y = y_is_big and middle_y or not y_is_big and parent.box[0][1]
            min_z = z_is_big and middle_z or not z_is_big and parent.box[0][2]

            max_x = x_is_big and parent.box[1][0] or not x_is_big and middle_x
            max_y = y_is_big and parent.box[1][1] or not y_is_big and middle_y
            max_z = z_is_big and parent.box[1][2] or not z_is_big and middle_z
            self.box = [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        self.status = Status.Final
        self.children = []
        self.req_votes_for_empty = req_votes_for_empty
        self.votes = 0

    def project_on_camera(self, camera):
        start = datetime.datetime.now().timestamp()
        v000 = (self.box[0][0], self.box[0][1], self.box[0][2])
        v100 = (self.box[1][0], self.box[0][1], self.box[0][2])
        v110 = (self.box[1][0], self.box[1][1], self.box[0][2])
        v010 = (self.box[0][0], self.box[1][1], self.box[0][2])
        v001 = (self.box[0][0], self.box[0][1], self.box[1][2])
        v011 = (self.box[0][0], self.box[1][1], self.box[1][2])
        v101 = (self.box[1][0], self.box[0][1], self.box[1][2])
        v111 = (self.box[1][0], self.box[1][1], self.box[1][2])
        vertices = [v000, v100, v110, v010, v001, v011, v101, v111]
        before_project = datetime.datetime.now().timestamp()
        projection_status = camera.project_cube(vertices)
        after_project = datetime.datetime.now().timestamp()

        if projection_status == 1:  # no intersection with mask
            self.votes += 1
            if self.votes >= self.req_votes_for_empty:
                self.status = Status.Empty
            else:
                self.status = Status.Refine
        if projection_status == 2 and not (self.status == Status.Empty):  # partially intersected with mask
            self.status = Status.Refine

        if projection_status == 3 and self.status == Status.Final:
            self.status = Status.Full
        finish = datetime.datetime.now().timestamp()
        if finish - start > 0.01:
            return after_project - before_project, self.status
        return None, self.status

    def print_tree(self, space, file=None):
        for children_node in self.children:
            if file is None:
                print(space + str(self.level) + " " + str(children_node.status))
            else:
                file.write(space + str(children_node.status) + '\n')
            children_node.print_tree(space + "  ", file)
