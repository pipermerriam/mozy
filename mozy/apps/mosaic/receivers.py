import uuid

from PIL import Image

from mozy.apps.mosaic.models import (
    SourceImageTile,
    StockImageTile,
)
from mozy.apps.mosaic.utils import (
    decompose_an_image,
    convert_image_to_django_file,
    extract_pixel_data_from_image,
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
        tile = SourceImageTile(
            main_image=instance,
            upper_left_x=box_coords[0],
            upper_left_y=box_coords[1],
            tile_data=extract_pixel_data_from_image(tile_image),
        )
        tile.tile_image.save(
            "{0}.png".format(str(uuid.uuid4())),
            convert_image_to_django_file(tile_image),
            save=True
        )
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
                tile_data=extract_pixel_data_from_image(tile_im),
            )

            stock_image_tile.tile_image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(tile_im),
                save=True,
            )
            tile_im.close()
