import cv2
import numpy as np


class Mask:
    def __init__(self, image):
        ret, self.thresh_mask = cv2.threshold(image, 127, 255, 0)
        self.image = self.thresh_mask // 128
        self.image = 1 - self.image
        cv2.sumElems(self.image)
        self.sum_image = cv2.integral(self.image)
        self.contour = None

    def find_contour(self):
        image, contours, hierarchy = cv2.findContours(self.thresh_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = None
        for contour in contours:
            if largest_contour is None or len(contour) > len(largest_contour):
                largest_contour = contour
        self.contour = largest_contour
        return largest_contour

    def get_area(self, rect):
        min_x = rect[0][0]
        max_x = rect[1][0]
        min_y = rect[0][1]
        max_y = rect[1][1]
        if min_x < 0 or min_y < 0 or max_x > 5999 or max_y > 3999:
            return -1
        max_x += 1
        max_y += 1
        right_bottom = self.sum_image[max_y + 1][max_x + 1]  # (max_y, max_x)
        right_top = self.sum_image[min_y][max_x + 1]  # (min_y, max_x)
        left_bottom = self.sum_image[max_y + 1][min_x]  # (max_y, min_x)
        left_top = self.sum_image[min_y][min_x]  # (min_y, min_x)
        area = right_bottom - right_top - left_bottom + left_top
        return area

