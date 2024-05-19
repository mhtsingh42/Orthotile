# Orthotile
Introducing a powerful Python library tailored for seamless manipulation of high-resolution Orthomosaic TIFF images, designed specifically to optimize Computer Vision tasks.

# Orthotile

Orthotile is a Python library designed for efficient manipulation of high-resolution Orthomosaic TIFF images, tailored specifically for Computer Vision tasks.

## Usage Example

### 1. Generating Tiles from Orthomosaic TIFF Image:

```python
import orthotile

# Initialize the Tiler class with the path to the orthomosaic TIFF image and the output folder path
otiles = orthotile.Tiler(orthomosaic_image_path="orthomosaic_image.tiff", output_folderpath=".")

# Generate tiles of a specified dimension
otiles.generate_tiles(tile_dimensions=512)
```

### 2. Stitching Tiles Back to Orthomosaic Image:

```python
import orthotile

# Initialize the Stitcher class with the path to the folder containing tiles,
# the dimensions of the orthomosaic image, and the size of the tiles
stitcher = orthotile.Stitcher(
    tiles_folder_path=".",
    orthomosaic_channel_width=57588,
    orthomosaic_channel_height=47222,
    tiles_size=512,
)

# Stitch tiles back to the orthomosaic image and optionally clean up the tiles
stitcher.stitch(cleanup_tiles=True)
```

### 3. Combined Workflow for Generating and Stitching Tiles:

```python
import orthotile

# Initialize the Tiler class with the orthomosaic TIFF image path and the output folder path
otiles = orthotile.Tiler(orthomosaic_image_path="orthomosaic_image.tiff", output_folderpath=".")

# Generate tiles of a specified dimension
otiles.generate_tiles(tile_dimensions=512)

# Pass Tiler class parameters to the Stitcher class

# Initialize the Stitcher class with metadata from the Tiler class directly
stitcher = orthotile.Stitcher(**otiles.get_metadata())

# Stitch tiles back to the orthomosaic image and optionally clean up the tiles
stitcher.stitch(cleanup_tiles=True)
```

## Module Installation

To install from the source, simply run:

```sh
python -m pip install .
```
```
