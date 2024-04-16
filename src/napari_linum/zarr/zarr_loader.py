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


def get_extension(fpath):
    return str(path.basename(fpath).split(".")[-1]).lower()


class ZarrLoader(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        self._zarr_path = FileEdit(label="Zarr Path", mode='d')
        self._resolution = FloatSpinBox(label="Resolution (um)", value=10.0)
        self._zarr = None

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
                self._type,
                self._resolution,
                self._load_data_button,
            ]
        )

    def _scale(self):
        res = self._resolution.value
        return (res, res, res)

    def _load(self):
        self._clear_message()
        if not path.exists(self._zarr_path.value):
            self._update_message('File does not exist')
            return
        try:
            ext = get_extension(self._zarr_path.value)
            if self._type.value == "labels":
                self._load_zarr_labels()
            elif self._type.value == "data":
                if ext == "zarr": self._open_zarr_data()
                elif ext == "omezarr": self._open_omezarr_data()
                else:
                    self._update_message('Unsupported file format')
                    return
        except Exception as e:
            print(e)
            self._update_message('Error loading Zarr Data')
            return

        self._viewer.scale_bar.visible = True
        self._viewer.scale_bar.unit = "um"

    def _open_omezarr_data(self):
        root = zarr.open(self._zarr_path.value, mode="r")
        n_scales = len(root)
        imin = root[n_scales-1][:].min()
        imax = np.percentile(root[n_scales-1][:], 99.9)

        self._viewer.open(
            self._zarr_path.value, 
            plugin='napari-ome-zarr', 
            name=get_name(self._zarr_path.value), 
            scale=self._scale(),
            colormap="magma",
            contrast_limits=[imin, imax]
        )

    def _open_zarr_data(self):
        self._viewer.add_image(
            zarr.open(self._zarr_path.value, mode="r"), 
            scale=self._scale(), 
            colormap="magma", 
            name=get_name(self._zarr_path.value)
        )
    
    def _load_zarr_labels(self):
        self._viewer.add_labels(
            zarr.load(self._zarr_path.value), 
            name=get_name(self._zarr_path.value), 
            scale=self._scale()
        )

