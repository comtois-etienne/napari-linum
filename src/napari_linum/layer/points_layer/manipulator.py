from typing import TYPE_CHECKING

from magicgui.widgets import PushButton

from ..manipulator import LayerManipulator

from ..layer_utils import (
    add_points_to_labels,
    reindex_labels,
)

if TYPE_CHECKING:
    import napari


class PointsLayerManipulator(LayerManipulator):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer.annotation = "napari.layers.Points"
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
        result = add_points_to_labels(
            self._source_layer.value.data, 
            self._output_layer.value.data
        )
        result = reindex_labels(result)
        self._save_output(result)

