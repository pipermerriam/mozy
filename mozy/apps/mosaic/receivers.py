import uuid

from PIL import Image

from mozy.apps.mosaic.models import (
    StockImageTile,
)
from mozy.apps.mosaic.utils import (
    convert_image_to_django_file,
    extract_pixel_data_from_image,
)
from mozy.apps.mosaic.tasks import (
    create_source_image_tiles as create_source_image_tiles_task,
)


def create_source_tiles(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return
    create_source_image_tiles_task(instance.pk)


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
