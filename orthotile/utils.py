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

from PIL import Image, ImageChops
from itertools import product
import os
import sys
import glob
import pathlib


def get_img_filelist(dir_out, pattern="r*.tiff"):
    image_paths = glob.glob(os.path.join(dir_out, pattern))
    image_paths = [
        (
            int(os.path.basename(image).split("_")[1]),
            int(os.path.basename(image).split("_")[2].split(".")[0]),
        )
        for image in image_paths
    ]
    image_paths.sort()
    return image_paths


def tile_rgb(arr, dir_out, d=256, pref="", ext=".tiff", compression=None, quality=100):
    img = Image.fromarray(arr)
    w, h = img.size
    grid = product(range(0, h - h % d, d), range(0, w - w % d, d))
    for i, j in grid:
        box = (j, i, j + d, i + d)
        out = os.path.join(dir_out, f"{pref}_{i}_{j}{ext}")
        cropped = img.crop(box)
        if ImageChops.invert(cropped).getbbox():
            cropped.save(out, compression=compression, quality=quality)


def tile_alpha(
    img_files, arr, dir_out, d=256, pref="", ext=".tiff", compression=None, quality=100
):
    img = Image.fromarray(arr)
    w, h = img.size
    grid = product(range(0, h - h % d, d), range(0, w - w % d, d))
    for i, j in grid:
        box = (j, i, j + d, i + d)
        out = os.path.join(dir_out, f"{pref}_{i}_{j}{ext}")
        cropped = img.crop(box)
        if (i, j) in img_files:
            cropped.save(out, compression=compression, quality=quality)


def channels_to_RGBA(img_files, dir_out, ext=".tiff", compression=None, quality=100):
    for i, j in img_files:
        r = Image.open(os.path.join(dir_out, f"r_{i}_{j}{ext}"))
        g = Image.open(os.path.join(dir_out, f"g_{i}_{j}{ext}"))
        b = Image.open(os.path.join(dir_out, f"b_{i}_{j}{ext}"))
        a = Image.open(os.path.join(dir_out, f"a_{i}_{j}{ext}"))
        rgb = Image.merge("RGBA", (r, g, b, a))
        rgb.save(
            os.path.join(dir_out, f"rgba_{i}_{j}{ext}"),
            compression=compression,
            quality=quality,
        )


def delete_file_safe(file_path):
    try:
        dfile = pathlib.Path(file_path)
        if sys.version_info >= (3, 8, 0):
            dfile.unlink(missing_ok=True)
        else:
            dfile.exists() and dfile.unlink()
    except Exception as e:
        print(str(e))


def delete_tiles(img_files, dir_out, ext=".tiff"):
    for i, j in img_files:
        delete_file_safe(os.path.join(dir_out, f"rgba_{i}_{j}{ext}"))


def delete_channel_files(img_files, dir_out, ext=".tiff"):
    for i, j in img_files:
        delete_file_safe(os.path.join(dir_out, f"r_{i}_{j}{ext}"))
        delete_file_safe(os.path.join(dir_out, f"g_{i}_{j}{ext}"))
        delete_file_safe(os.path.join(dir_out, f"b_{i}_{j}{ext}"))
        delete_file_safe(os.path.join(dir_out, f"a_{i}_{j}{ext}"))
