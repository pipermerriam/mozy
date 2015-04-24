import uuid
import logging

from PIL import Image

from django.db.models import Q
from django.db import (
    transaction,
    IntegrityError,
)
from django.utils import timezone

from huey.djhuey import (
    db_task,
    periodic_task,
    crontab,
)

from mozy.apps.mosaic.models import (
    NormalizedSourceImage,
    SourceImageTile,
    MosaicImage,
)
from mozy.apps.mosaic.utils import (
    decompose_an_image,
    convert_image_to_django_file,
    extract_pixel_data_from_image,
)
from mozy.apps.mosaic.backends import (
    get_mosaic_backend,
)


logger = logging.getLogger(__file__)


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
        queue_source_image_tile_tasks(source_image_pk)


@db_task()
def queue_source_image_tile_tasks(source_image_pk):
    """
    Queues tasks to match the source image tiles with stock image tiles.
    """
    source_image = NormalizedSourceImage.objects.get(pk=source_image_pk)
    for tile_id in source_image.all_tiles.values_list('pk', flat=True):
        match_single_source_image_tile(tile_id)


@db_task()
def match_single_source_image_tile(source_image_tile_pk):
    tile = SourceImageTile.objects.get(pk=source_image_tile_pk)

    matcher = get_mosaic_backend()(tile.main_image)

    stock_id, match_similarity = matcher(tile.numpy_tile_data)

    with transaction.atomic():
        SourceImageTile.objects.select_for_update().filter(
            (
                Q(stock_tile_match_difference__isnull=True) |
                Q(stock_tile_match_difference__lt=match_similarity)
            ),
            Q(pk=tile.pk),
        ).update(
            stock_tile_match_id=stock_id,
            stock_tile_match_difference=match_similarity,
        )
    logger.info(
        "Matched tile:%s with stock_image:%s - %s",
        tile.pk, stock_id, match_similarity,
    )


@periodic_task(crontab(minute='*'))
def create_pending_mosaics():
    """
    Look for any NormalizedSourceImage instances that are ready for mosaic
    composition and create a pending mosaic image as well as triggering a task
    to compose it.
    """
    source_images_ready_for_composition = NormalizedSourceImage.objects.filter(
        mosaic_images__isnull=True,
    ).exclude(
        all_tiles__stock_tile_match__isnull=True,
    ).distinct()
    for source_image in source_images_ready_for_composition:
        stock_tiles_hash = source_image.get_stock_tile_hash()
        source_image.mosaic_images.create(
            tile_size=40,
            stock_tiles_hash=stock_tiles_hash,
            status=MosaicImage.STATUS_PENDING,
        )


@periodic_task(crontab(minute='*'))
def queue_mosaic_images_for_composition():
    """
    Search for any mosaic images that are pending or have errored during
    composition.
    """
    mosaic_images_to_queue = MosaicImage.objects.filter(
        Q(status=MosaicImage.STATUS_PENDING) |
        Q(
            status=MosaicImage.STATUS_COMPOSING,
            updated_at__lte=MosaicImage.get_errored_datetime(),
        )
    ).distinct()
    with transaction.atomic():
        mosaic_images_to_queue.select_for_update().update(
            status=MosaicImage.STATUS_PENDING,
            updated_at=timezone.now(),
        )
    for mosaic_image_pk in mosaic_images_to_queue.values_list('pk', flat=True):
        compose_mosaic_image(mosaic_image_pk)


@db_task()
def compose_mosaic_image(mosaic_image_pk):
    with transaction.atomic():
        lock_aquired = MosaicImage.objects.select_for_update().filter(
            pk=mosaic_image_pk,
            status=MosaicImage.STATUS_PENDING,
        ).update(
            status=MosaicImage.STATUS_COMPOSING,
            updated_at=timezone.now(),
        )

    if not lock_aquired:
        logger.error("Unable to aquire lock on MosaicImage: %s", mosaic_image_pk)
        return

    mosaic_image = MosaicImage.objects.get(pk=mosaic_image_pk)
    mosaic_image.image.compose_mosaic(
        compose_tile_size=mosaic_image.tile_size,
        mosaic_image=mosaic_image,
    )
