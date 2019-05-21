import PhotoScan as ps
import numpy as np

from thin_module.camera import Camera
from thin_module.bounding_box import BoundingBox


class ObjectData:
    def __init__(self):
        self.chunk = ps.app.document.chunk
        labels = [# '2018_04_09_Nadir_g201b20087_f001_0018.JPG',
                  '2018_04_09_Nadir_g201b20087_f001_0714.JPG',
                  # '2018_04_09_Nadir_g201b20087_f001_0713.JPG',
                  # '2018_04_09_Nadir_g201b20087_f001_0715.JPG',
                  '2018_04_09_Nadir_g201b20087_f001_0716.JPG',
                  '2018_04_09_Nadir_g201b20087_f001_0748.JPG',
                  '2018_04_09_Nadir_g201b20087_f001_0749.JPG',
                  '2018_04_09_Nadir_g201b20087_f001_1445.JPG',
                  # '2018_04_09_Nadir_g201b20087_f001_0750.JPG'
                  '2018_04_09_Nadir_g201b20087_f001_1446.JPG',
                  '2018_04_09_Nadir_g201b20087_f001_1447.JPG'
                  ]
        for ps_cam in self.chunk.cameras:
            if ps_cam.label in labels:
                ps_cam.selected = True
        self.cameras = []
        self.init_cameras()
        self.camera_contours = self._get_camera_contours()
        self.bounding_box = BoundingBox(self.camera_contours)
        # self.generate_shape()

    def _get_camera_contours(self):
        camera_contours = []
        for camera in self.cameras:
            camera_contour = camera.find_contour_3d()
            camera_contours.append(camera_contour)
        return camera_contours

    def init_cameras(self):
        for ps_cam in self.chunk.cameras:
            if ps_cam.selected:
                camera = Camera(ps_cam, self.chunk)
                self.cameras.append(camera)

    def gen_shape_group(self, groups, name):
        shape_group = None
        for sg in groups:
            if sg.label == name:
                shape_group = sg

        if shape_group is None:
            shape_group = self.chunk.shapes.addGroup()
            shape_group.label = name
            shape_group.color = (30, 239, 30)
        return shape_group

    def gen_shape(self, curve, name, shape_group):
        shape = self.chunk.shapes.addShape()
        shape.label = name
        for camera in self.chunk.cameras:
            if camera.selected:
                shape.attributes["Photo"] = camera.label
        shape.type = ps.Shape.Type.Polyline
        shape.group = shape_group
        shape.vertices = curve
        shape.has_z = True

    def generate_shape(self):
        bounds = self.bounding_box.bounds
        shape_groups = self.chunk.shapes.groups
        group = self.gen_shape_group(shape_groups, "Boxes")
        self.chunk.shapes.remove(self.chunk.shapes.items())

        min_x = bounds[0][0]
        min_y = bounds[0][1]
        min_z = bounds[0][2]
        max_x = bounds[1][0]
        max_y = bounds[1][1]
        max_z = bounds[1][2]
        v000 = (min_x, min_y, min_z)
        v100 = (max_x, min_y, min_z)
        v110 = (max_x, max_y, min_z)
        v010 = (min_x, max_y, min_z)
        v001 = (min_x, min_y, max_z)
        v011 = (min_x, max_y, max_z)
        v101 = (max_x, min_y, max_z)
        v111 = (max_x, max_y, max_z)
        bottom = np.asarray([v000, v010, v110, v100, v000])
        top = np.asarray([v001, v011, v111, v101, v001])
        left = np.asarray([v000, v001, v011, v010, v000])
        right = np.asarray([v100, v101, v111, v110, v100])
        forward = np.asarray([v000, v001, v101, v100, v000])
        backward = np.asarray([v010, v011, v111, v110, v010])
        faces = np.asarray([bottom, top, left, right, forward, backward])
        for face in faces:
            self.gen_shape(face, "face", group)

    def world_to_geocenter(self, point):
        geocenter = self.chunk.crs.unproject(ps.Vector(point))
        return [geocenter.x, geocenter.y, geocenter.z]

    def print_stats(self):
        for camera in self.cameras:
            print(camera.get_stats())
