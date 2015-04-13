import uuid

from scipy.misc import imread

from PIL import Image

from mozy.apps.mosaic.models import (
    MosaicTile,
)
from mozy.apps.mosaic.utils import (
    decompose_an_image,
    convert_image_to_django_file,
    cast_scipy_array_to_python,
)


def create_mosaic_tiles(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return

    if instance.image.file.closed:
        instance.image.file.open()

    tile_data = decompose_an_image(
        Image.open(instance.image.file),
        tile_size=instance.tile_size,
    )

    for box_coords, tile_image in tile_data.items():
        tile = MosaicTile(
            main_image=instance,
            upper_left_x=box_coords[0],
            upper_left_y=box_coords[1],
            tile_data=tile_data,
        )
        tile.tile_image.save(
            "{0}.png".format(str(uuid.uuid4())),
            convert_image_to_django_file(tile_image),
        )
        if tile.tile_image.file.closed:
            tile.tile_image.open()
        with tile.tile_image.file as fp:
            tile.tile_data = cast_scipy_array_to_python(imread(fp))
        tile_image.close()
