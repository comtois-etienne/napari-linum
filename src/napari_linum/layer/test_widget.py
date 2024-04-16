from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, Container, create_widget, PushButton
import numpy as np

from .manipulator import LayerManipulator


if TYPE_CHECKING:
    import napari


class TestWidget(LayerManipulator):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._test_button = PushButton(text="Test Button")
        self._test_button.changed.connect(self._test)

        self.extend(
            [
                self._test_button,
            ]
        )

    # action method
    def _test(self):
        print('Test Button Pressed')
        print(self._source_layer.value)
        print(type(self._source_layer.value))
        print(self._source_layer.value.data)
        print(self._source_layer.value.data.shape)

