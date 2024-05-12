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

if TYPE_CHECKING:
    import napari


def get_center(img):
    mask = img > filters.threshold_otsu(img)
    y, x = np.where(mask)
    y, x = int(np.median(y)), int(np.median(x))
    return y, x


def square_pad(img, center, dim):
    y, x = center
    top = abs(dim - y)
    bottom = abs(dim - (img.shape[0] - y))
    left = abs(dim - x)
    right = abs(dim - (img.shape[1] - x))
    return np.pad(img, ((top, bottom), (left, right)), 'constant', constant_values=(0, 0))


def stack_pad(img_stack, dim):
    y, x = img_stack.shape[1] // 2, img_stack.shape[2] // 2
    top = abs(dim - y)
    bottom = abs(dim - (img_stack.shape[1] - y))
    left = abs(dim - x)
    right = abs(dim - (img_stack.shape[2] - x))
    return np.pad(img_stack, ((0, 0), (top, bottom), (left, right)), 'constant', constant_values=(0, 0))


def get_image_path(folder_path, index):
    images_names = [f for f in os.listdir(folder_path) if not f.startswith('.')]
    images_names = sorted(images_names)
    if index >= len(images_names):
        return None
    return images_names[index]


class SliceReader(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)
        self._img_path = FileEdit(label="Images Folder Path", mode='d')

        self._layer_name = LineEdit(
            label="Layer Name",
            value="Slices",
        )

        self._reverse_order_button = CheckBox(label="Reverse Images Order", value=False)
        self._reverse_order_button.enabled = False # todo implement

        self._otsu_button = CheckBox(label="Otsu Centering", value=False)

        self._refresh_rate_button = FloatSpinBox(label="Refresh Rate (s)", value=1.0, min=0.0, max=3600.0, step=1.0)

        self._load_data_button = PushButton(text="Start Reading Slices")
        self._load_data_button.changed.connect(self._load)

        self._reset_button = PushButton(text="Reset")
        self._reset_button.changed.connect(self._reset)
        self._reset_button.enabled = False

        self._is_loading = False
        self._images_names = []
        self._stack = None
        self._shape = 0
        self._current_image = 0

        self.extend(
            [
                self._img_path,
                self._layer_name,
                self._reverse_order_button,
                self._otsu_button,
                # self._refresh_rate_button,
                self._load_data_button,
                self._reset_button,
            ]
        )

    def _freeze(self):
        self._img_path.enabled = False
        self._layer_name.enabled = False
        self._reset_button.enabled = True
        self._otsu_button.enabled = False

    def _stop(self):
        self._is_loading = False
        self._load_data_button.text = "Start Reading Slices"

    def _reset(self):
        self._stop()

        self._images_names = []
        self._stack = None
        self._shape = 0
        self._current_image = 0

        self._img_path.enabled = True
        self._layer_name.enabled = True
        self._reset_button.enabled = False
        self._otsu_button.enabled = True

    def _update_shape(self, img, center):
        y, x = center
        self._shape = max(y, x, img.shape[0] - y, img.shape[1] - x, self._shape)

    def _action(self):
        img_path = get_image_path(self._img_path.value, self._current_image)
        if img_path is None:
            self._update_message("No more images to read")
            # print("No more images to read")
            return False
        self._update_message(f"Reading New Slice")
        # print("Reading slices")
        self._current_image += 1
        self._images_names.append(img_path)
        img = iio.imread(os.path.join(self._img_path.value, img_path))
        center = get_center(img) if self._otsu_button.value else (img.shape[0] // 2, img.shape[1] // 2)
        self._update_shape(img, center)
        img = square_pad(img, center, self._shape)
        img = np.expand_dims(img, axis=0)
        if self._stack is None:
            self._stack = img
            self._viewer.add_image(self._stack, name=self._layer_name.value)
        else:
            self._stack = stack_pad(self._stack, self._shape)
            self._stack = np.concatenate((self._stack, img), axis=0)
            self._viewer.layers[self._layer_name.value].data = self._stack

        return True

    # @thread_worker
    def _load(self):
        self._clear_message()
        self._is_loading = True
        self._load_data_button.text = "Update New Slices"
        self._freeze()

        while self._action():
            pass

        # Define a function to run the while loop in a separate thread
        # @thread_worker
        # def run_loop():
        #     while self._is_loading:
        #         start = time.time()
        #         self._action()
        #         delta = time.time() - start
        #         time.sleep(max(0, self._refresh_rate_button.value - delta))

        # Start the thread
        # self._thread = threading.Thread(target=run_loop)
        # self._thread.start()
        # run_loop()
