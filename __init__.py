# -*- coding: utf-8 -*-
"""
===============================================
orthotile library source-code is deployed under the Apache 2.0 License:

Copyright (c) 2023 Abhishek Thakur(@abhiTronix) <abhi.una12@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
===============================================
"""

"""
A python library for manipulating high-res Orthomosaic TIFF image for Computer Vision tasks.
"""

from osgeo import gdal
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import (
    tile_rgb,
    tile_alpha,
    channels_to_RGBA,
    get_img_filelist,
    delete_channel_files,
    delete_tiles,
)
from datetime import datetime
from itertools import product
from PIL import Image
from tqdm import tqdm
import numpy as np
import pathlib
import os

__author__ = "Abhishek Singh Thakur"
__copyright__ = "Copyright (c) 2023 Abhishek Thakur(@abhiTronix) <abhi.una12@gmail.com>"
__license__ = "Apache-2.0 license"
__email__ = "abhi.una12@gmail.com"
__version__ = "0.1.2"

valid_channels = ["r", "g", "b", "a"]
channels_indexes = {"r": 1, "g": 2, "b": 3, "a": 4}


class Tiler(object):
    """Interface for the Orthomosaic TIFF Image Tiler."""

    def __init__(
        self,
        orthomosaic_image_path=None,
        output_folderpath=".",
    ):
        assert not (
            orthomosaic_image_path is None
        ), "No input. Kindly provide a valid orthomosaic TIFF image file."
        orthomosaic_img_path = pathlib.Path(orthomosaic_image_path)
        assert orthomosaic_img_path.is_file() and orthomosaic_img_path.suffix in [
            ".tif",
            ".tiff",
        ], f"Image file `{orthomosaic_img_path.resolve()}` doesn't exist or invalid, Kindly provide a valid orthomosaic TIFF image file."
        try:
            self.dataset = gdal.Open(str(orthomosaic_img_path.resolve()))
        except Exception as e:
            print(str(e))
            raise ValueError(
                f"Invalid input. Failed to open `{orthomosaic_img_path.name}` image."
            )
        self.out = pathlib.Path(output_folderpath).resolve()
        self.channel_shape = None
        self.tiles_size = None

    def __generate_tile_rgba(self, channel, tile_dimensions):
        """Internal method for multithreaded image tiler"""
        assert channel in valid_channels, "Invalid channel detected"
        band = self.dataset.GetRasterBand(channels_indexes[channel])
        ch_array = np.asarray(band.ReadAsArray())
        if self.channel_shape is None:
            self.channel_shape = ch_array.shape
        if self.tiles_size is None:
            self.tiles_size = tile_dimensions
        if channel == "a":
            img_files = get_img_filelist(self.out)
            tile_alpha(img_files, ch_array, self.out, pref=channel, d=tile_dimensions)
        else:
            tile_rgb(ch_array, self.out, pref=channel, d=tile_dimensions)
        # cleanup
        del band
        del ch_array

    def generate_tiles(self, tile_dimensions=256):
        """Method for generating tiles of given dimensions from a original orthomosaic TIFF image.

        Parameters:
        tile_dimensions (int): dimension of output tiles
        """
        print("Generating channels files. Please wait...")
        # multithreaded tiling
        with tqdm(total=len(valid_channels)) as pbar:
            with ThreadPoolExecutor(max_workers=1) as ex:
                futures = [
                    ex.submit(self.__generate_tile_rgba, channel, tile_dimensions)
                    for channel in valid_channels
                ]
                for future in as_completed(futures):
                    result = future.result()
                    pbar.update(1)

        img_files = get_img_filelist(self.out)
        try:
            print("Merging channel files...")
            channels_to_RGBA(img_files, self.out)
            print("Cleaning leftover files...")
            delete_channel_files(img_files, self.out)
        except Exception as e:
            raise RuntimeError(str(e))
        print("Tiling operation completed successfully!!!")

    @property
    def get_tile_coordinates(self):
        """
        A property object that dumps coordinates of each valid tile.

        **Returns:** list
        """
        return get_img_filelist(self.out)

    @property
    def get_metadata(self):
        """
        A property object that dumps output metadata.

        **Returns:** dict
        """
        return {
            "tiles_folder_path": self.out,
            "orthomosaic_channel_width": self.channel_shape[1],
            "orthomosaic_channel_height": self.channel_shape[0],
            "tiles_size": self.tiles_size,
        }


class Stitcher(object):
    """Interface for the Orthomosaic TIFF Image tiles Stitcher."""

    def __init__(
        self,
        tiles_folder_path,
        orthomosaic_channel_width,
        orthomosaic_channel_height,
        tiles_size,
    ):
        # check if tiles_folder_path is provided
        assert not (
            tiles_folder_path is None
        ), "No input. Kindly provide a valid orthomosaic TIFF tiles folder path."
        self.tiles_folder_path = pathlib.Path(tiles_folder_path)

        # verify and extract RGBA TIFF tiles
        assert self.tiles_folder_path.is_dir() and any(
            self.tiles_folder_path.iterdir()
        ), f"Folder {self.tiles_folder_path.resolve()} doesn't exist or empty, Kindly provide a valid orthomosaic TIFF tiles folder path."
        all_tiles = self.tiles_folder_path.glob("rgba*.tiff")
        # extract coordinates from tiles filenames
        self.__tiles_coor = [
            (
                int(os.path.basename(tile).split("_")[1]),
                int(os.path.basename(tile).split("_")[2].split(".")[0]),
            )
            for tile in all_tiles
        ]
        # sort them
        self.__tiles_coor.sort()

        # verify and extract original width and height of orthomosaic image
        assert isinstance(
            orthomosaic_channel_width, int
        ), f"Invalid {orthomosaic_channel_width} value!"
        assert isinstance(
            orthomosaic_channel_height, int
        ), f"Invalid {orthomosaic_channel_height} value!"
        org_w = orthomosaic_channel_width
        org_h = orthomosaic_channel_height

        # verify tile size
        assert (
            isinstance(tiles_size, int) and tiles_size > 5
        ), f"Invalid {tiles_size} value!"
        self.tiles_size = tiles_size

        # calculate new width and height
        # new_width = org_w - org_w % tiles_size
        # new_height = org_h - org_w % tiles_size
        # create new blank RGBA image with new width and height
        self.new_ortho_image = Image.new("RGBA", (org_w, org_h))

        # calculate orthomosaic image grid
        self.orthomosaic_grid = product(
            range(0, org_h - org_h % tiles_size, tiles_size),
            range(0, org_w - org_w % tiles_size, tiles_size),
        )

    def __stitch_tiles(self, tile_coordinate):
        """Internal method for multithreaded image tiler"""
        assert not tile_coordinate is None, "Invalid tile coordinates"
        (i, j) = tile_coordinate
        if (i, j) in self.__tiles_coor:
            tile_image = Image.open(
                os.path.join(self.tiles_folder_path, f"rgba_{i}_{j}.tiff")
            )
            box = (j, i, j + self.tiles_size, i + self.tiles_size)
            self.new_ortho_image.paste(tile_image, box)

    def stitch(self, extension=".png", cleanup_tiles=False):
        """Method for stitching multiple tiles into a original orthomosaic image.

        Parameters:
        extension (string): extension of orthomosaic tile. Default is `.png`.
        cleanup_tiles (bool): Cleanup tiles after stitching?
        """
        print("Stitching tiles. Please wait...")
        # multithreaded stitching
        with tqdm(total=len(valid_channels)) as pbar:
            with ThreadPoolExecutor(max_workers=1) as ex:
                futures = [
                    ex.submit(self.__stitch_tiles, tile_coor)
                    for tile_coor in self.orthomosaic_grid
                ]
                for future in as_completed(futures):
                    result = future.result()
                    pbar.update(1)
        try:
            time_str = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
            save_path = os.path.join(
                self.tiles_folder_path, f"{time_str}_rgba{extension}"
            )
            print(f"Saving orthomosaic file at {save_path}...")
            self.new_ortho_image.save(save_path, compress_level=1)
            if cleanup_tiles:
                print("Cleaning leftover files...")
                tiles_paths = get_img_filelist(self.tiles_folder_path, pattern="rgba_*")
                delete_tiles(
                    tiles_paths,
                    self.tiles_folder_path,
                )
                del self.new_ortho_image
        except Exception as e:
            raise RuntimeError(str(e))
        print("Stitching operation completed successfully!!!")
