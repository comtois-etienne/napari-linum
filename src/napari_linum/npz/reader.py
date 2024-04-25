from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, ComboBox

from ..widget import LinumWidget
from ..utils import get_name, get_extension
from linumpy.io.npz import read_numpy_data

if TYPE_CHECKING:
    import napari


class NpzReader(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        self._file_path = FileEdit(label="Path", mode='r')

        self._type = ComboBox(
            label="Type",
            choices=["data", "labels"],
            value="data",
        )
        self._load_data_button = PushButton(text="Open Numpy Array")
        self._load_data_button.changed.connect(self._load)

        self.extend(
            [
                self._file_path,
                self._type,
                self._load_data_button,
            ]
        )

    def _load(self):
        self._clear_message()
        try:
            if self._type.value == "labels":
                self._load_labels()
            elif self._type.value == "data":
                self._load_data()
        except Exception as e:
            print(e)
            self._update_message('Error loading file')

    def _load_labels(self):
        data, _ = read_numpy_data(self._file_path.value)
        self._viewer.add_labels(data, name=get_name(self._file_path.value))

    def _load_data(self):
        data, _ = read_numpy_data(self._file_path.value)
        self._viewer.add_image(data, name=get_name(self._file_path.value))

