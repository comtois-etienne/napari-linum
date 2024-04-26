from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, ComboBox
import zarr
import numpy as np
from os import path

from ..widget import LinumWidget
from ..utils import get_name, get_extension

if TYPE_CHECKING:
    import napari


class ZarrReader(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        self._zarr_path = FileEdit(label="Zarr Path", mode='d')
        self._zarr_path.changed.connect(self._path_changed)

        self._resolution_z = FloatSpinBox(label="Z Resolution (um)", value=10.0, min=0.1, max=1000.0)
        self._resolution_y = FloatSpinBox(label="Y Resolution (um)", value=10.0, min=0.1, max=1000.0)
        self._resolution_x = FloatSpinBox(label="X Resolution (um)", value=10.0, min=0.1, max=1000.0)
        self._resolution_z.changed.connect(self._same_button_changed)

        self._same_button = CheckBox(label="Same Resolution", value=True)
        self._same_button.changed.connect(self._same_button_changed)

        self._type = ComboBox(
            label="Type",
            choices=["data", "labels"],
            value="data",
        )
        self._ignore_button = CheckBox(label="Ignore Resolution", value=False)
        self._ignore_button.changed.connect(self._ignore_button_changed)

        self._load_data_button = PushButton(text="Open Zarr File")
        self._load_data_button.changed.connect(self._load)

        self._ignore_button_changed()

        self.extend(
            [
                self._zarr_path,
                self._type,
                self._resolution_z,
                self._resolution_y,
                self._resolution_x,
                self._same_button,
                self._ignore_button,
                self._load_data_button,
            ]
        )

    def _same_button_changed(self):
        if self._same_button.value:
            self._resolution_y.value = self._resolution_z.value
            self._resolution_x.value = self._resolution_z.value
        self._resolution_y.enabled = (not self._ignore_button.value) and (not self._same_button.value)
        self._resolution_x.enabled = (not self._ignore_button.value) and (not self._same_button.value)

    def _ignore_button_changed(self):
        if self._ignore_button.value:
            self._resolution_z.enabled = False
            self._resolution_y.enabled = False
            self._resolution_x.enabled = False
            self._same_button.enabled = False
        else:
            self._same_button.enabled = True
            self._resolution_z.enabled = True
            self._same_button_changed()

    def _path_changed(self):
        ext = get_extension(self._zarr_path.value)
        if ext == 'omezarr':
            self._type.value = "data"
            self._type.enabled = False
            self._resolution_z.enabled = False
            self._resolution_y.enabled = False
            self._resolution_x.enabled = False
            self._ignore_button.enabled = False
            self._same_button.enabled = False
        else:
            self._type.enabled = True
            self._ignore_button.enabled = True
            self._same_button.enabled = True
            self._ignore_button_changed()

    def _scale(self):
        return [self._resolution_z.value, self._resolution_y.value, self._resolution_x.value] if not self._ignore_button.value else None
    
    def _add_scale_bar(self):
        self._viewer.scale_bar.visible = True
        self._viewer.scale_bar.unit = "um"

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
        if not self._ignore_button.value:
            self._add_scale_bar()

    def _open_omezarr_data(self):
        root = zarr.open(self._zarr_path.value, mode="r")
        n_scales = len(root)
        imin = root[n_scales-1][:].min()
        imax = np.percentile(root[n_scales-1][:], 99.9)

        self._viewer.open(
            self._zarr_path.value, 
            plugin='napari-ome-zarr', 
            name=get_name(self._zarr_path.value), 
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

