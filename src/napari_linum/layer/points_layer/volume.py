from typing import TYPE_CHECKING

from magicgui.widgets import PushButton, create_widget, Label, ComboBox, CheckBox, LineEdit, FloatSpinBox

from ..converter import LayerConverter
from ...utils import replace_text_in_parenthesis as rtp
from ..layer_utils import (
    add_points_to_labels,
    reindex_labels,
    is_instance,
)

import numpy as np

if TYPE_CHECKING:
    import napari


CHOICES = [
    'From 2 Points',
    'From 3 Points',
    'Auto Random Cube',
]


class PointsLayerVolume(LayerConverter):

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer.annotation = "napari.layers.Points"
        self._output_layer.annotation = "napari.layers.Labels"
        self._output_layer.changed.connect(self._output_change)

        self._function_dropdown = ComboBox(
            label="Function",
            choices=CHOICES,
            value=CHOICES[-1],
        )
        self._function_dropdown.changed.connect(self._function_dropdown_change)

        self._full_height_checkbox = CheckBox(
            text="Full Height",
            value=False,
        )
        self._full_height_checkbox.changed.connect(self._function_dropdown_change)

        self._scale_checkbox = CheckBox(
            text="Preserve ZYX Scale (Pixel)",
            value=True,
        )
        self._scale_checkbox.changed.connect(self._function_dropdown_change)

        self._unit_checkbox = CheckBox(
            text="Unit : (pixel) / um",
            value=True,
        )
        self._unit_checkbox.changed.connect(self._unit_checkbox_change)

        self._text_input = LineEdit(
            label="Depth (pixel)",
            value="200",
        )

        self._label_value = FloatSpinBox(label="Label", value=1, min=1, max=4096, step=1)

        self._action_button = PushButton(text="Generate Volume")
        self._action_button.changed.connect(self._action)

        self._function_dropdown_change()

        self.extend(
            [
                self._full_height_checkbox,
                self._scale_checkbox,
                self._unit_checkbox,
                self._text_input,
                self._function_dropdown,
                self._label_value,
                self._action_button,
            ]
        )

    def _output_change(self):
        if self._output_layer.value is not None:
            self._label_value.value = np.max(self._output_layer.value.data) + 1
        else:
            self._label_value.value = 1

    def _on_refresh(self):
        self._clear_message()
        self._output_change()

    def _unit_checkbox_change(self):
        if self._unit_checkbox.value:
            self._unit_checkbox.text = "Unit : (pixel) | um"
            self._scale_checkbox.text = rtp(self._scale_checkbox.text, "Pixel")
            self._text_input.label = rtp(self._text_input.label, "pixel")
        else:
            self._unit_checkbox.text = "Unit : pixel | (um)"
            self._scale_checkbox.text = rtp(self._scale_checkbox.text, "um")
            self._text_input.label = rtp(self._text_input.label, "um")

    def _function_dropdown_change(self):
        if self._function_dropdown.value == CHOICES[0]:
            self._text_input.enabled = not (self._scale_checkbox.value or self._full_height_checkbox.value)
            self._text_input.label = "Depth (x)"
        elif self._function_dropdown.value == CHOICES[1]:
            self._text_input.enabled = False
        elif self._function_dropdown.value == CHOICES[2]:
            self._text_input.enabled = True
            self._text_input.label = "Size (x)"
        self._source_layer.enabled = self._function_dropdown.value != CHOICES[-1]
        if not self._scale_checkbox.value:
            self._unit_checkbox.value = True
            self._unit_checkbox.enabled = False
        else:
            self._unit_checkbox.enabled = True
        self._unit_checkbox_change()

    def _action(self):
        self._clear_message()
        ndim = self._output_layer.value.ndim
        self._conditional_message(ndim != 3, "Output layer must be 3D")

        if self._function_dropdown.value == CHOICES[0]:
            points = np.round(self._source_layer.value.data).astype(int)[:2]
            self._to_volume_2_points(points)
        elif self._function_dropdown.value == CHOICES[1]:
            self._user_message("Not implemented yet")
            # self._to_volume_3_points(points)
        elif self._function_dropdown.value == CHOICES[2]:
            self._auto_random_cubes()
        self._output_change()

    # action method
    def _to_volume_2_points(self, points):
        scale = self._output_layer.value.scale
        if not self._scale_checkbox.value:
            scale = [1, 1, 1]
        
        y_diff = abs(points[1][1] - points[0][1]) * scale[1]
        x_diff = abs(points[1][2] - points[0][2]) * scale[2]
        size = max(int(y_diff), int(x_diff))
        top_layer = points[0][0]
        bot_layer = max((top_layer - int(size/scale[0])), 0)

        depth = ''.join(filter(str.isdigit, self._text_input.value))
        if depth != "" and not (self._scale_checkbox.value or self._full_height_checkbox.value):
            depth = int(depth)
            bot_layer = max((top_layer - int(depth/scale[0])), 0)

        if self._full_height_checkbox.value:
            shape = self._output_layer.value.data.shape
            top_layer = shape[0] - 1
            bot_layer = 0

        y = points[0][1]
        x = points[0][2]
        label = int(self._label_value.value)

        for i in range(bot_layer, top_layer+1):
            self._output_layer.value.data[i, y:y+int(size/scale[1]), x:x+int(size/scale[2]) ] = label

        # napari refresh layers
        self._output_layer.value.refresh()


    # def _to_volume_3_points(self, points):
    #     pass

    def _auto_random_cubes(self):
        shape = self._output_layer.value.data.shape
        scale = self._output_layer.value.scale
        if not self._scale_checkbox.value:
            scale = [1.0, 1.0, 1.0]
        
        size = ''.join(filter(str.isdigit, self._text_input.value))
        size = int(size) if size != "" else 200

        ratio = scale[2] if self._unit_checkbox.value else 1
        z_size = int( size / scale[0] * ratio )
        y_size = int( size / scale[1] * ratio )
        x_size = int( size / scale[2] * ratio )

        random_z = shape[0]-1
        if z_size < shape[0]:
            random_z = np.random.randint(z_size, shape[0])
        random_y = np.random.randint(0, shape[1]-y_size)
        random_x = np.random.randint(0, shape[2]-x_size)

        self._to_volume_2_points(
            np.array([
                [random_z, random_y, random_x], 
                [random_z, random_y+y_size, random_x+x_size]
            ])
        )

