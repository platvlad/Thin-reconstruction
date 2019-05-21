import PhotoScan as ps
import numpy as np


def ps_mat_to_np(matrix):
    a0 = np.asarray(matrix.row(0))
    a1 = np.asarray(matrix.row(1))
    a2 = np.asarray(matrix.row(2))
    a3 = np.asarray(matrix.row(3))
    return np.asarray([a0, a1, a2, a3])


def mulp(matrix, vector):
    vector = np.concatenate((vector, [1]), axis=0)
    result = np.dot(matrix, vector)
    return (result / result[3])[:3]
