from typing import TYPE_CHECKING

from magicgui.widgets import PushButton

from ..converter import LayerConverter

from ..layer_utils import (
    add_points_to_labels,
    reindex_labels,
    is_instance,
)

if TYPE_CHECKING:
    import napari


class PointsLayerConverter(LayerConverter):

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
            (not is_instance(self._output_layer.value, 'labels')), 
            "Output must be a Labels layer"): 
            return
        self._save_data('Rasterize')
        result = add_points_to_labels(
            self._source_layer.value.data, 
            self._output_layer.value.data
        )
        # result = reindex_labels(result)
        self._save_output(result)

