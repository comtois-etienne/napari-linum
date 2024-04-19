from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, Container, create_widget, PushButton
import numpy as np

from ..converter import LayerConverter

from ..layer_utils import (
    binarize_array,
    label_array,
    reindex_labels,
    add_labels,
)

if TYPE_CHECKING:
    import napari


class LabelsLayerConverter(LayerConverter):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer.annotation = "napari.layers.Labels"
        self._output_layer.annotation = "napari.layers.Labels"

        self._binarize_button = PushButton(text="Binarize")
        self._binarize_button.changed.connect(self._binarize)

        self._auto_label_button = PushButton(text="Auto Label")
        self._auto_label_button.changed.connect(self._auto_label)

        self._reindex_button = PushButton(text="Reindex")
        self._reindex_button.changed.connect(self._reindex)

        self._transfer_labels_button = PushButton(text="Transfer Labels")
        self._transfer_labels_button.changed.connect(self._transfer_labels)

        self.extend(
            [
                self._binarize_button,
                self._auto_label_button,
                self._reindex_button,
                self._transfer_labels_button,
            ]
        )

    # action method
    def _binarize(self):
        self._save_data('Binarize')
        bin_array = self._source_layer.value.data
        bin_array = binarize_array(bin_array)
        self._save_output(bin_array)

    # action method
    def _auto_label(self):
        self._save_data('Auto Label')
        array = self._source_layer.value.data
        labeled_array = label_array(array)
        self._save_output(labeled_array)

    # action method
    def _reindex(self):
        self._save_data('Reindex')
        array = self._source_layer.value.data
        new_arr = reindex_labels(array)
        self._save_output(new_arr)

    # action method
    def _transfer_labels(self):
        self._save_data('Transfer Labels')
        source_layer_data = self._source_layer.value.data
        output_layer_data = self._output_layer.value.data
        new_arr = add_labels(source_layer_data, output_layer_data)
        self._save_output(new_arr)

