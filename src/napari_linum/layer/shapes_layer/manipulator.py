from typing import TYPE_CHECKING

from magicgui.widgets import PushButton
import numpy as np

from ..manipulator import LayerManipulator

from ..layer_utils import (
    add_labels,
)

if TYPE_CHECKING:
    import napari


class ShapesLayerManipulator(LayerManipulator):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer.annotation = "napari.layers.Shapes"
        self._output_layer.annotation = "napari.layers.Layer"

        self._rasterize_button = PushButton(text="Rasterize")
        self._rasterize_button.changed.connect(self._resterize)

        self.extend(
            [
                self._rasterize_button,
            ]
        )

    # action method
    def _resterize(self):
        if self._usage_error(
            (str(self._output_layer.value) != 'Labels'), 
            "Output must be a Labels layer"): 
            return
        self._save_data('Rasterize')
        shapes = self._source_layer.value
        raster = shapes.to_labels()
        shape = self._output_layer.value.data.shape
        raster = np.pad(raster, ((0, shape[0] - raster.shape[0]), (0, shape[1] - raster.shape[1])), constant_values=0)
        result = add_labels(raster, self._output_layer.value.data)
        self._save_output(result)

