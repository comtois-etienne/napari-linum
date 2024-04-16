from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget
from ..widget import LinumWidget


if TYPE_CHECKING:
    import napari


def get_revert_button_text(last_action):
    if last_action is None:
        return "< Action Pending >"
    return f"< Revert '{last_action}' >"


class LayerManipulator(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        
        self._source_layer = create_widget(
            label="Source :", annotation="napari.layers.Layer"
        )
        self._output_layer = create_widget(
            label="Output :", annotation="napari.layers.Layer"
        )

        # save state
        self._st_source_data = None
        self._st_output_data = None
        self._st_source_layer_name = None
        self._st_output_layer_name = None
        self._st_last_action = None

        # check box
        self._allow_revert = CheckBox(text="Allow Action Revert")
        self._allow_revert.changed.connect(self._clear_data)

        self._revert_button = PushButton(text=get_revert_button_text(self._st_last_action))
        self._revert_button.changed.connect(self._revert_data)

        self._spacer = EmptyWidget()

        self._hide_source_layer = CheckBox(text="Hide Source After Action", value=True)

        self.extend(
            [
                self._source_layer, 
                self._output_layer,
                self._revert_button,
                self._allow_revert,
                self._spacer,
                self._hide_source_layer,
            ]
        )

    def _refresh_layer(self):
        self._output_layer.value.refresh()

    def _hide_source(self):
        if self._source_layer.value.name != self._output_layer.value.name:
            self._toggle_layer_visibility(self._source_layer.value)

    def _save_output(self, data):
        self._output_layer.value.data = data
        if self._hide_source_layer.value:
            self._hide_source()
        self._refresh_layer()

    def _clear_data(self):
        self._st_source_data = None
        self._st_output_data = None
        self._st_source_layer_name = None
        self._st_output_layer_name = None
        self._st_last_action = None
        self._revert_button.text = get_revert_button_text(self._st_last_action)

    def _usage_error(self, condition, message):
        if self._conditional_message(condition, message):
            self._clear_data()
        return condition

    def _save_data(self, action):
        self._clear_message()
        if not self._allow_revert.value:
            return
        self._st_source_layer_name = self._source_layer.value.name
        self._st_output_layer_name = self._output_layer.value.name
        self._st_source_data = self._source_layer.value.data
        self._st_output_data = self._output_layer.value.data
        self._st_last_action = action
        self._revert_button.text = get_revert_button_text(self._st_last_action)

    # action method
    def _revert_data(self):
        self._clear_message()
        if self._usage_error(
            (not self._allow_revert.value), 
            "Action revert is disabled"):
            return
        if self._usage_error(
            (self._st_last_action is None), 
            "No action to revert"):
            return
        self._viewer.layers[self._st_source_layer_name].data = self._st_source_data
        self._viewer.layers[self._st_output_layer_name].data = self._st_output_data
        self._clear_data()

