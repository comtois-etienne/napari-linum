from typing import TYPE_CHECKING

from magicgui.widgets import Container, Label, PushButton
import time

if TYPE_CHECKING:
    import napari


class LinumWidget(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        self._user_message = Label()

        self._refresh_button = PushButton(text="Refresh")
        self._refresh_button.changed.connect(self._called_on_refresh)

        self.extend(
            [
                self._refresh_button,
                self._user_message,
            ]
        )

    def _toggle_layer_visibility(self, layer):
        layer.visible = not layer.visible

    def _update_message(self, message: str):
        self._user_message.value = message
        self._user_message.label = time.strftime("%H:%M:%S") + " :"

    def _clear_message(self):
        self._user_message.value = ""
        self._user_message.label = ""

    def _conditional_message(self, condition: bool, message: str):
        if condition:
            self._update_message(message)
        return condition
    
    def _called_on_refresh(self):
        self._clear_message()
        self._on_refresh()
    
    def _on_refresh(self):
        # to be implemented by subclass
        self._update_message("Nothing to refresh")
        pass

