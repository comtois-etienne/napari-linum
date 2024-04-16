from scipy.ndimage import label
import numpy as np


def binarize_array(array):
    bin_array = np.where(array > 0, 1, array)
    bin_array = bin_array.astype(int)
    return bin_array


def label_array(array):
    array = binarize_array(array)
    labeled_array, _ = label(array)
    return labeled_array


def reindex_labels(array):
    _, inverse = np.unique(array, return_inverse=True)
    new_arr = inverse.reshape(array.shape)
    return new_arr


def add_labels(source_layer: np.array, output_layer: np.array):
    current = np.max(output_layer)
    source_layer = source_layer + current
    source_layer = np.where(source_layer == current, 0, source_layer)
    source_layer = np.maximum(output_layer, source_layer)
    return reindex_labels(source_layer)


def add_points_to_labels(points, labels):
    points = np.round(points).astype(int)
    current = np.max(labels) + 1
    labels[points[:, 0], points[:, 1]] = np.arange(current, current + len(points))
    return labels

