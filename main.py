#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""napari-linum"""

from importlib.metadata import distribution
import argparse
import os


def check_conda_env():
    active_env = os.getenv('CONDA_DEFAULT_ENV')
    if active_env != 'napari_linum':
        print(f"Warning: You are not in the 'napari_linum' conda environment. You are in the '{active_env}' environment.")
        print("Please run : conda activate napari_linum")
        exit(1)


def check_dependencies():
    dependencies = [
        'scikit-learn', 
        'pandas', 
        'opencv', 
        'jupyterlab', 
        'matplotlib', 
        'pytorch', 
        'pip', 
        'torchvision', 
        'exifread', 
        'gdal', 
        'seaborn', 
        'geopandas', 
        'plotly', 
        'zarr', 
        'numcodecs',
        'segment-anything',
        'napari',
        'napari-segment-anything',
        'napari-ome-zarr',
        'linumpy',
        'napari-linum',
    ]

    not_installed = []

    for dependency in dependencies:
        try:
            distribution(dependency)
        except Exception:
            print(f"{dependency} is NOT installed.")
            not_installed.append(dependency)
    
    # if napari and linumpy are not installed, then print message
    if 'napari' in not_installed or 'linumpy' in not_installed or 'napari-linum' in not_installed:
        print("Please install all conda dependencies in the environment 'napari_linum' before running the application.")
        exit(1)


def run_napari_linum():
    import napari
    viewer = napari.Viewer()
    napari.run()


def main():
    check_conda_env()
    check_dependencies()
    run_napari_linum()


if __name__ == "__main__":
    main()

