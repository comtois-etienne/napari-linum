from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, ComboBox
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

        # drop down with zarr or ome-zarr options
        self._format = ComboBox(
            label="Format",
            choices=["zarr", "ome-zarr"],
            value="zarr",
        )

        self._type = ComboBox(
            label="Type",
            choices=["data", "labels"],
            value="data",
        )

        self._load_data_button = PushButton(text="Open Zarr File")
        self._load_data_button.changed.connect(self._load)

        self.extend(
            [
                self._zarr_path,
                self._format,
                self._type,
                self._resolution,
                self._load_data_button,
            ]
        )

    def _scale(self):
        res = self._resolution.value
        return (res, res, res)

    def _load(self):
        if self._type.value == "data":
            self._load_zarr_data()
        elif self._type.value == "labels":
            self._load_zarr_labels()

    def _load_zarr_data(self):
        try:
            zarr_path = str(self._zarr_path.value)
            name = get_name(zarr_path)
            self._zarr = zarr.open(zarr_path, mode="r")
            self._viewer.add_image(self._zarr, scale=self._scale(), colormap="magma", name=name)
            self._viewer.scale_bar.visible = True
            self._viewer.scale_bar.unit = "um"
            self._clear_message()
        except Exception as e:
            print(e)
            self._update_message('Error loading Zarr file')
    
    def _load_zarr_labels(self):
        try:
            name = get_name(self._zarr_path.value)
            self._zarr = zarr.load(self._zarr_path.value)
            self._viewer.add_labels(self._zarr, name=name, scale=self._scale())
            self._clear_message()
        except Exception as e:
            print(e)
            self._update_message('Error loading Zarr file')

