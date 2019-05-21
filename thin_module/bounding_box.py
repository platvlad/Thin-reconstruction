import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.geometry.polygon import LinearRing


class BoundingBox:
    def __init__(self, contours):
        self.contours = contours
        self.footing = self._get_footing()
        self.bounds = self.expand_box()
        print("bounds = ", self.bounds)

    def _get_footing(self):
        shared = None
        for contour in self.contours:
            points = np.asarray(contour)
            ring = LinearRing(points)
            poly = Polygon(ring)
            if shared is None:
                shared = poly
            else:
                try:
                    shared = shared.intersection(poly)
                except shapely.geos.TopologicalError:
                    break
        bounds = list(shared.exterior.coords)
        return bounds

    def expand_box(self):
        #  initialize bounding box around footing points
        xs = [point[0] for point in self.footing]
        ys = [point[1] for point in self.footing]
        zs = [point[2] for point in self.footing]
        min_x = min(xs) - 0.25
        max_x = max(xs) + 0.25
        min_y = min(ys) - 0.25
        max_y = max(ys) + 0.25
        min_z = min(zs) - 0.1
        max_z = max(zs) + 0.7
        bounds = np.array([[min_x, min_y, min_z], [max_x, max_y, max_z]])
        return bounds
