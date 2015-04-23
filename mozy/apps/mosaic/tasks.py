import uuid

from PIL import Image

from django.db import (
    transaction,
    IntegrityError,
)

from huey.djhuey import (
    db_task,
)

from mozy.apps.mosaic.models import (
    NormalizedSourceImage,
    SourceImageTile,
)
from mozy.apps.mosaic.utils import (
    decompose_an_image,
    convert_image_to_django_file,
    extract_pixel_data_from_image,
)
from mozy.apps.mosaic import matcher


@db_task()
def create_source_image_tiles(source_image_pk):
    source_image = NormalizedSourceImage.objects.get(pk=source_image_pk)

    if source_image.image.file.closed:
        source_image.image.file.open()

    tile_data = decompose_an_image(
        Image.open(source_image.image.file),
        tile_size=source_image.tile_size,
    )

    for box_coords, tile_image in tile_data.items():
        already_exists = SourceImageTile.objects.filter(
            main_image=source_image,
            upper_left_x=box_coords[0],
            upper_left_y=box_coords[1],
        ).exists()
        if already_exists:
            continue
        tile = SourceImageTile(
            main_image=source_image,
            upper_left_x=box_coords[0],
            upper_left_y=box_coords[1],
            tile_data=extract_pixel_data_from_image(tile_image),
        )
        try:
            with transaction.atomic():
                tile.tile_image.save(
                    "{0}.png".format(str(uuid.uuid4())),
                    convert_image_to_django_file(tile_image),
                    save=True
                )
        except IntegrityError:
            pass
        tile_image.close()

    if not source_image.mosaic_images.exists():
        match_source_image_tiles(source_image_pk)


@db_task()
def match_source_image_tiles(source_image_pk):
    """
    Work in progress.
    """
    source_image = NormalizedSourceImage.objects.get(pk=source_image_pk)
    matcher.create_mosaic(source_image)
