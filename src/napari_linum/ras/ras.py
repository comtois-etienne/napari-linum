from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, ComboBox, LineEdit
import time
# import threading
# from napari.qt.threading import thread_worker
import numpy as np
from skimage import filters
import os
import imageio.v2 as iio

from ..widget import LinumWidget
from ..layer.layer_utils import get_layer_by_name

if TYPE_CHECKING:
    import napari


POINT_LAYERS = ['anterieur', 'posterieur', 'superieur', 'inferieur']


class Ras(LinumWidget):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self.create_layers()

        self._info_anterieur = Label()
        self._info_posterieur = Label()
        self._info_superieur = Label()
        self._info_inferieur = Label()
        self._on_refresh()

        self._convert_button = PushButton(text="Convert")
        self._convert_button.changed.connect(self._convert)

        self.extend(
            [
                self._info_anterieur,
                self._info_posterieur,
                self._info_superieur,
                self._info_inferieur,
                self._convert_button,
            ]
        )

    def create_layers(self):
        #ne fonctionn pas correctement - utiliser les layers du UI de napari
        point = [0,0,0]
        for point_layer in POINT_LAYERS:
            if get_layer_by_name(self._viewer, point_layer) is None:
                self._viewer.add_points(point, name=point_layer)


    def _info_points(self, info_button, layer_name):
        layer = get_layer_by_name(self._viewer, layer_name)
        info_button.label = layer_name
        info_button.value = layer.data

    def _on_refresh(self):
        self._info_points(self._info_anterieur, POINT_LAYERS[0])
        self._info_points(self._info_posterieur, POINT_LAYERS[1])
        self._info_points(self._info_superieur, POINT_LAYERS[2])
        self._info_points(self._info_inferieur, POINT_LAYERS[3])

    def _convert(self):
        print('convert')
        pass
