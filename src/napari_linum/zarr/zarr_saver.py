from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox
import zarr
import numpy as np
from os import path

from ..widget import LinumWidget

if TYPE_CHECKING:
    import napari


class ZarrSaver(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer = create_widget(
            label="Source :", annotation="napari.layers.Layer"
        )
        self._zarr_path = FileEdit(label="Save Directory", mode='d')

        self._save_button = PushButton(text="Save Zarr")
        self._save_button.changed.connect(self._save_zarr)

        self.extend(
            [
                self._source_layer,
                self._zarr_path,
                self._save_button,
            ]
        )

    def _save_zarr(self):
        annotations = self._source_layer.value.data
        layer_name = self._source_layer.value.name
        zarr_path = str(self._zarr_path.value)
        z = zarr.zeros(shape=annotations.shape, dtype=annotations.dtype)
        z[:] = annotations
        save_path = path.join(zarr_path, f'{layer_name}.zarr')
        zarr.save(save_path, z)

