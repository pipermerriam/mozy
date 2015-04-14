import uuid

from scipy.misc import imread

from PIL import Image

from mozy.apps.mosaic.models import (
    MosaicTile,
    StockImageTile,
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
        )
        tile.tile_image.save(
            "{0}.png".format(str(uuid.uuid4())),
            convert_image_to_django_file(tile_image),
            save=False
        )
        if tile.tile_image.file.closed:
            tile.tile_image.open()
        with tile.tile_image.file as fp:
            tile.tile_data = cast_scipy_array_to_python(imread(fp))
        tile.save()
        tile_image.close()


def create_stock_tiles(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return

    if instance.image.file.closed:
        instance.image.file.open()

    with instance.image.file as fp:
        im = Image.open(fp)
        for tile_size, _ in StockImageTile.TILE_SIZE_CHOICES:
            tile_im = im.copy()
            tile_im.thumbnail((tile_size, tile_size))

            stock_image_tile = StockImageTile(
                stock_image=instance,
                tile_size=tile_size,
            )

            stock_image_tile.tile_image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(tile_im),
                save=False,
            )
            if stock_image_tile.tile_image.file.closed:
                stock_image_tile.tile_image.open()

            with stock_image_tile.tile_image.file as t_fp:
                tile_data = cast_scipy_array_to_python(imread(t_fp))
                stock_image_tile.tile_data = tile_data
            stock_image_tile.save()
