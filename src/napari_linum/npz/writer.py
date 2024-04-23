from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, ComboBox

from ..widget import LinumWidget
from ..utils import get_name, get_extension
from linumpy.io.npz import write_numpy

from ..layer.layer_utils import (
    get_layers,
    get_layer_by_name,
)

from os import path

if TYPE_CHECKING:
    import napari


class NpzWriter(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer = ComboBox(
            label="Source",
            choices=get_layers(viewer, ["image", "labels"]),
        )
        self._file_path = FileEdit(label="Save Directory", mode='d')

        self._button = PushButton(text="Save Numpy Array")
        self._button.changed.connect(self._save)

        self.extend(
            [
                self._source_layer,
                self._file_path,
                self._button,
            ]
        )

    def _on_refresh(self):
        self._clear_message()
        self._source_layer.choices = get_layers(self._viewer, ["image", "labels"])
        self._update_message('Refreshed layer list')

    def _save(self):
        self._clear_message()
        try:
            layer = get_layer_by_name(self._viewer, self._source_layer.value)
            file_path = path.join(self._file_path.value, layer.name)
            write_numpy(file_path, data=layer.data)
        except Exception as e:
            print(e)
            self._update_message('Error saving file')



