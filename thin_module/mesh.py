class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def add_cube(self, box):  # axis-aligned box in format [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        vertex_num = len(self.vertices) + 1
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    self.vertices.append([box[i][0], box[j][1], box[k][2]])
        self.faces.append([vertex_num, vertex_num + 2, vertex_num + 6, vertex_num + 4])  # z = 0
        self.faces.append([vertex_num + 5, vertex_num + 7, vertex_num + 3, vertex_num + 1])  # z = 1
        self.faces.append([vertex_num + 4, vertex_num + 5, vertex_num + 1, vertex_num])  # y = 0
        self.faces.append([vertex_num + 2, vertex_num + 3, vertex_num + 7, vertex_num + 6])  # y = 1
        self.faces.append([vertex_num, vertex_num + 1, vertex_num + 3, vertex_num + 2])  # x = 0
        self.faces.append([vertex_num + 6, vertex_num + 7, vertex_num + 5, vertex_num + 4])  # x = 1

    def scale(self):
        min_x = min([point[0] for point in self.vertices])
        max_x = max([point[0] for point in self.vertices])
        min_y = min([point[1] for point in self.vertices])
        max_y = max([point[1] for point in self.vertices])
        min_z = min([point[2] for point in self.vertices])
        max_z = max([point[2] for point in self.vertices])
        diam_x = max_x - min_x
        diam_y = max_y - min_y
        diam_z = max_z - min_z
        diam = max(diam_x, diam_y, diam_z)
        for point in self.vertices:
            point[0] = 50 * (point[0] - min_x) / diam
            point[1] = 50 * (point[1] - min_y) / diam
            point[2] = 50 * (point[2] - min_z) / diam

    def export(self, filename):
        print("exporting mesh")
        with open(filename, "w") as file:
            for point in self.vertices:
                file.write(
                    "v " + str(point[0]) + ' ' + str(point[1]) + ' ' + str(point[2]) + '\n')
            for face in self.faces:
                file.write("f " + str(face[0]) + ' ' + str(face[1]) + ' ' + str(face[2]) + ' ' + str(face[3]) + '\n')
