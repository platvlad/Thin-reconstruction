import PhotoScan as ps
import numpy as np
from thin_module.mask import Mask
import datetime
import thin_module.convert as convert


class Camera:
    def __init__(self, ps_cam, chunk):
        self.ps_cam = ps_cam
        self.chunk = chunk
        self.cam_inv_transform = None
        self.compute_cam_inv_transform()
        self.points = list()
        self.mask = None
        self.sensor = self.ps_cam.sensor
        self.times = []
        self.px_0 = None
        self.px_dx = None
        self.px_dy = None
        self.px_dz = None

    def find_contour_3d(self):
        self._get_mask()
        contour_2d = self.mask.find_contour()
        point_cloud = self.chunk.dense_cloud
        for pixel_list in contour_2d:
            for pixel in pixel_list:
                pixel_vector = ps.Vector(pixel)
                destination_camera = self.sensor.calibration.unproject(pixel_vector)  # 3d point on ray (camera space)
                destination_chunk = self.ps_cam.transform.mulp(destination_camera)  # 3d point on ray (chunk space)
                target_point = point_cloud.pickPoint(self.ps_cam.center, destination_chunk)  # 3d point (chunk space)
                self.points.append(target_point)
        return self.points

    def compute_cam_inv_transform(self):
        mat = self.ps_cam.transform.inv()
        self.cam_inv_transform = convert.ps_mat_to_np(mat)

    def _get_mask(self):
        mask = self.ps_cam.mask
        mask_image = mask.image()
        mask_image_byte = mask_image.tostring()
        mask_image_byte = np.asarray(list(mask_image_byte), dtype='uint8')
        mask_image_byte = mask_image_byte.reshape((4000, 6000))
        self.mask = Mask(mask_image_byte)

    def get_pixel_by_point(self, point_geogr):
        camera_point = convert.mulp(self.cam_inv_transform, point_geogr)
        pixel = self.sensor.calibration.project(camera_point)
        pixel = np.rint(pixel)
        pixel = pixel.astype(int)
        return pixel

    def get_stats(self):
        if self.times:
            return np.median(np.array(self.times)), np.var(np.array(self.times)), min(self.times), max(self.times)
        return 0

    def project_cube(self, points):
        start = datetime.datetime.now().timestamp()
        pixels = [self.get_pixel_by_point(point) for point in points]
        x_comp = [pixel[0] for pixel in pixels]
        y_comp = [pixel[1] for pixel in pixels]
        min_x = min(x_comp)
        max_x = max(x_comp)
        min_y = min(y_comp)
        max_y = max(y_comp)
        rectangle = [[min_x, min_y], [max_x, max_y]]
        area = self.mask.get_area(rectangle)
        if area == -1:  # index out of range
            return 4
        projection_area = (max_x - min_x) * (max_y - min_y)
        if projection_area < 1:  # empty projection
            return 4

        if area == 0:  # no intersection with mask
            return 1
        if area == (max_x - min_x + 1) * (max_y - min_y + 1):
            return 3
        finish = datetime.datetime.now().timestamp()
        self.times.append(finish - start)
        return 2  # partly intersected with mask
