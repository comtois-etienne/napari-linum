from scipy.ndimage import label
import numpy as np
import napari


def binarize_array(array):
    bin_array = np.where(array > 0, 1, array)
    bin_array = bin_array.astype(int)
    return bin_array


def label_array(array):
    array = binarize_array(array)
    if len(array.shape) == 3:
        for i in range(array.shape[0]):
            array[i], _ = label(array[i])
    else:
        array, _ = label(array)
    return array


def _reindex_labels(array):
    _, inverse = np.unique(array, return_inverse=True)
    new_arr = inverse.reshape(array.shape)
    return new_arr


def reindex_labels(array):
    if len(array.shape) == 3:
        for i in range(array.shape[0]):
            array[i] = _reindex_labels(array[i])
    else:
        array = _reindex_labels(array)
    return array


def add_labels(source_layer: np.array, output_layer: np.array):
    current = np.max(output_layer)
    source_layer = source_layer + current
    source_layer = np.where(source_layer == current, 0, source_layer)
    source_layer = np.maximum(output_layer, source_layer)
    return reindex_labels(source_layer)


def add_points_to_labels(points, labels):
    dim = np.ndim(labels)
    points = np.round(points).astype(int)
    current = np.max(labels) + 1
    arranges = np.arange(current, current + len(points))
    if dim == 2:
        labels[points[:, 0], points[:, 1]] = arranges
    elif dim == 3:
        labels[points[:, 0], points[:, 1], points[:, 2]] = arranges
    elif dim == 4:
        labels[points[:, 0], points[:, 1], points[:, 2], points[:, 3]] = arranges
    return labels


def labels_to_points(labels):
    points = np.argwhere(labels)
    return points


def get_layer_type(layer):
    return type(layer).__name__.lower().split('.')[-1]


def is_instance(layer, layer_type):
    layer_class = getattr(napari.layers, layer_type.capitalize(), None)
    if layer_class is not None:
        return isinstance(layer, layer_class)
    return False


def get_layers(viewer: napari.Viewer, layer_types: list = ['image', 'labels', 'points', 'shapes', 'surface', 'tracks', 'vectors']):
    def get_layers_of_type(viewer: napari.Viewer, layer_type: str):
        layer_class = getattr(napari.layers, layer_type.capitalize(), None)
        if layer_class is not None:
            return [layer for layer in viewer.layers if isinstance(layer, layer_class)]
        return []
    layers = []
    for layer_type in layer_types:
        layers.extend(get_layers_of_type(viewer, layer_type))
    return layers


def get_layer_by_name(viewer: napari.Viewer, layer_name: str):
    for layer in viewer.layers:
        if str(layer.name) == str(layer_name):
            return layer
    return None


def shapes_to_labels(viewer: napari.Viewer, shapes: napari.layers.Shapes):
    layers = get_layers(viewer, ['labels', 'image'])
    shape = layers[0].data.shape
    raster = shapes.to_labels()
    raster = np.pad(raster, ((0, shape[0] - raster.shape[0]), (0, shape[1] - raster.shape[1])), constant_values=0)
    return raster

