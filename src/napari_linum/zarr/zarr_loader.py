from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox
import zarr
import numpy as np
from os import path

from ..widget import LinumWidget

if TYPE_CHECKING:
    import napari


def get_name(fpath):
    return path.basename(fpath).split(".")[0]


class ZarrLoader(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        self._zarr_path = FileEdit(label="Zarr Path", mode='d')
        self._resolution = FloatSpinBox(label="Resolution (um)", value=10.0)
        self._zarr = None

        self._load_data_button = PushButton(text="Load Zarr as Data")
        self._load_data_button.changed.connect(self._load_zarr_data)

        self._load_labels_button = PushButton(text="Load Zarr as Labels")
        self._load_labels_button.changed.connect(self._load_zarr_labels)

        self.extend(
            [
                self._zarr_path,
                self._resolution,
                self._load_data_button,
                self._load_labels_button,
            ]
        )

    def _load_zarr_data(self):
        try:
            resolution = float(self._resolution.value)
            zarr_path = str(self._zarr_path.value)
            name = get_name(zarr_path)
            self._zarr = zarr.open(zarr_path, mode="r")
            scale = (resolution, resolution, resolution)
            self._viewer.add_image(self._zarr, scale=scale, colormap="magma", name=name)
            self._viewer.scale_bar.visible = True
            self._viewer.scale_bar.unit = "um"
            self._clear_message()
        except Exception as e:
            print(e)
            self._update_message('Error loading Zarr file')
    
    def _load_zarr_labels(self):
        try:
            data_layer = self._viewer.layers[0]
            name = get_name(self._zarr_path.value)
            annotations = zarr.load(self._zarr_path.value)
            self._viewer.add_labels(annotations, name=name, scale=data_layer.scale)
            self._clear_message()
        except Exception as e:
            print(e)
            self._update_message('Error loading Zarr file')

