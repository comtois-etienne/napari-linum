from typing import TYPE_CHECKING

from magicgui.widgets import CheckBox, create_widget, PushButton, EmptyWidget, Label, FileEdit, FloatSpinBox, Select, ComboBox
import zarr
import numcodecs
import numpy as np
import os
from os import path

from linumpy.io.zarr import save_zarr

from ..widget import LinumWidget

if TYPE_CHECKING:
    import napari


def is_dir_empty(directory, ignore_hidden=True):
    if not path.exists(directory):
        return True
    files = os.listdir(directory)
    if ignore_hidden:
        files = [file for file in files if not file.startswith('.')]
    return not files


def compress_zarr(zarr_arr, method):
    # Create a compressor object based on the specified method
    if method == "none":
        return zarr_arr
    elif method == "gzip":
        compressor = numcodecs.GZip(level=1)
    elif method == "zstd":
        compressor = numcodecs.Zstd(level=1)
    elif method == "lz4":
        compressor = numcodecs.LZ4(level=1)
    elif method.startswith("blosc-"):
        blosc_method = method.split("-")[1]
        compressor = numcodecs.Blosc(cname=blosc_method, clevel=5, shuffle=numcodecs.Blosc.SHUFFLE)
    else:
        raise ValueError(f"Unsupported compression method: {method}")

    return zarr.array(zarr_arr, compressor=compressor)


class ZarrSaver(LinumWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__(viewer)

        self._source_layer = create_widget(
            label="Source :", annotation="napari.layers.Layer"
        )
        self._zarr_path = FileEdit(label="Save Directory", mode='d')
        self._save_path = None

        self._format = ComboBox(
            label="Format",
            choices=["zarr", "omezarr"],
            value="zarr",
        )

        self._compression = ComboBox(
            label="Compression",
            choices=["none", "gzip", "zstd", "lz4"] + [f"blosc-{x}" for x in numcodecs.blosc.list_compressors()],
            value="gzip",
        )

        self._overwrite = CheckBox(text="Overwrite", value=False)

        self._save_button = PushButton(text="Save Layer")
        self._save_button.changed.connect(self._save)

        self.extend(
            [
                self._source_layer,
                self._zarr_path,
                self._format,
                self._compression,
                self._overwrite,
                self._save_button,
            ]
        )

    def _update_path(self):
        layer_name = str(self._source_layer.value.name)
        zarr_path = str(self._zarr_path.value)
        current_ext = path.splitext(zarr_path)[1]
        zarr_path = zarr_path[:len(zarr_path)-len(current_ext)]
        if not zarr_path.endswith(layer_name):
            zarr_path = path.join(zarr_path, f'{layer_name}')
        self._save_path = f'{zarr_path}.{str(self._format.value)}'

    def _save(self):
        self._clear_message()
        self._update_path()

        if not self._overwrite.value and not is_dir_empty(self._save_path):
            self._update_message('File already exists. Enable overwrite to save.')
            return

        self._update_message('Saving Zarr file...')
        try:
            ext = str(self._format.value)
            if ext == "zarr":
                self._save_zarr()
            elif ext == "omezarr":
                self._save_omezarr()
        except Exception as e:
            self._update_message('Error saving file')
            print(e)
            return
        self._update_message('Zarr file saved')

    def _save_zarr(self):
        data = self._source_layer.value.data
        z = zarr.zeros(shape=data.shape, dtype=data.dtype)
        z[:] = data
        z = compress_zarr(z, self._compression.value)
        zarr.save(self._save_path, z)

    def _save_omezarr(self):
        data = self._source_layer.value.data
        resolution = self._source_layer.value.scale[0]
        scales = [resolution * 1e-3] * 3  # convert to mm
        save_zarr(data, self._save_path, scales=scales, overwrite=self._overwrite.value)

