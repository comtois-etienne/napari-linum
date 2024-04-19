from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, ComboBox
import numpy as np
from os import path
import imageio.v2 as iio

from PIL import Image
Image.MAX_IMAGE_PIXELS = None

from ..widget import LinumWidget
from ..utils import get_name, get_extension

_DEFAULT_MAX_IMAGE_PIXELS = 89478485

if TYPE_CHECKING:
    import napari


class OrthoReader(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        self._path_input = FileEdit(label="Path", mode='r')
        self._load_data_button = PushButton(text="Open Orthophoto")
        self._load_data_button.changed.connect(self._load)

        self.extend(
            [
                self._path_input,
                self._load_data_button,
            ]
        )

    def _open_ortho(self):
        img = iio.imread(self._path_input.value)
        # keep the first 3 channels
        img = img[..., :3]
        self._viewer.add_image(img, name=get_name(self._path_input.value))

    def _load(self):
        self._clear_message()
        if not path.exists(self._path_input.value):
            self._update_message('File does not exist')
            return
        try:
            Image.MAX_IMAGE_PIXELS = None
            self._open_ortho()
        except Exception as e:
            self._update_message(str(e))
        Image.MAX_IMAGE_PIXELS = _DEFAULT_MAX_IMAGE_PIXELS

