from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, Container, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox
import bak.zarr as zarr
import numpy as np
from os import path

if TYPE_CHECKING:
    import napari


class ZarrLoader(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        self._zarr_path = FileEdit(label="Zarr Path", mode='d')
        self._resolution = FloatSpinBox(label="Resolution (um)", value=10.0)
        self._zarr = None

        self._load_button = PushButton(text="Load Zarr")
        self._load_button.changed.connect(self._load_zarr)

        self.extend(
            [
                self._zarr_path,
                self._resolution,
                self._load_button,
            ]
        )

    def _load_zarr(self):
        resolution = float(self._resolution.value)
        zarr_path = str(self._zarr_path.value)
        name = path.basename(zarr_path).split(".")[0]
        self._zarr = zarr.open(zarr_path, mode="r")
        scale = (resolution, resolution, resolution)
        self._viewer.add_image(self._zarr, scale=scale, colormap="magma", name=name)
        self._viewer.scale_bar.visible = True
        self._viewer.scale_bar.unit = "um"

