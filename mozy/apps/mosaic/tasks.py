import uuid
import logging
import time

import excavator

from contexttimer import Timer

from django.db.models import Q
from django.db import (
    transaction,
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
from mozy.apps.mosaic.backends import (
    get_mosaic_backend,
)


logger = logging.getLogger(__file__)


@db_task()
def create_source_image_tiles(source_image_pk):
    source_image = NormalizedSourceImage.objects.get(pk=source_image_pk)

    with Timer() as timer:
        source_image.create_tiles()

    logger.info(
        "Took %s to create source image tiles for NormalizedSourceImage: %s",
        timer.elapsed,
        source_image_pk,
    )
    # go ahead and trigger tile matching
    queue_source_image_tiles_for_matching()


MATCH_BATCH_SIZE = excavator.env_int('MOSAIC_BATCH_SIZE', default=40)


@periodic_task(crontab(minute='*'))
def queue_source_image_tiles_for_matching():
    if SourceImageTile.objects.processing().exists():
        return

    logger.info("Queueing tiles for matching")
    for _ in range(20):
        match_souce_image_tiles()


@db_task()
def match_souce_image_tiles(tile_pk=None):
    if tile_pk:
        tile = SourceImageTile.objects.get(pk=tile_pk)
        with transaction.atomic():
            SourceImageTile.objects.select_for_update(
            ).update(
                updated_at=timezone.now(),
                task_lock=uuid.uuid4(),
            )

    else:
        start = time.time()
        while time.time() < start + 5:
            tile = SourceImageTile.objects.unmatched().first()
            if not tile:
                logger.info("No tiles to match")

            # get lock
            with transaction.atomic():
                lock_aquired = SourceImageTile.objects.unmatched(
                ).select_for_update(
                ).filter(
                    pk=tile.pk,
                ).update(
                    updated_at=timezone.now(),
                    task_lock=uuid.uuid4(),
                )
            if lock_aquired:
                break

    if lock_aquired:
        logger.info("Acquired lock on tile: %s", tile.pk)
    else:
        logger.info("Unable to acquire lock on tile: %s", tile.pk)

    with Timer() as timer:
        matcher = get_mosaic_backend()(tile.main_image)

        match_data = matcher((
            (tile.pk, tile.numpy_tile_data),
        ))
        if not match_data:
            logger.warning("Could not find match for tile: %s", tile.pk)
            return

        _, stock_id, match_similarity = match_data[0]

        with transaction.atomic():
            success = tile.main_image.tiles.select_for_update(
            ).filter(
                (
                    Q(stock_tile_match_difference__isnull=True) |
                    Q(stock_tile_match_difference__lt=match_similarity)
                ),
                Q(pk=tile.pk),
            ).update(
                stock_tile_match_id=stock_id,
                stock_tile_match_difference=match_similarity,
                updated_at=timezone.now(),
            )
            if not success:
                logger.warning(
                    "Expected to update StockImageTile: %s - Existing "
                    "stock_tile_match_id %s with difference %s.  Replacing "
                    "with stock_tile_match_id %s and difference %s",
                    tile.pk,
                    tile.stock_tile_match_id,
                    tile.stock_tile_match_difference,
                    stock_id,
                    match_similarity,
                )
    logger.info(
        "Took %s to match SourceImageTile: %s for NormalizedSourceImage: %s",
        timer.elapsed,
        tile.pk,
        tile.main_image.pk,
    )


#@periodic_task(crontab(minute='*/5'))
#def create_pending_mosaics():
#    """
#    Look for any NormalizedSourceImage instances that are ready for mosaic
#    composition and create a pending mosaic image as well as triggering a task
#    to compose it.
#    """
#    source_images_ready_for_composition = NormalizedSourceImage.objects.filter(
#        mosaic_images__isnull=True,
#    ).exclude(
#        tiles__stock_tile_match__isnull=True,
#    ).distinct()
#    for source_image in source_images_ready_for_composition:
#        stock_tiles_hash = source_image.get_stock_tile_hash()
#        source_image.mosaic_images.create(
#            tile_size=40,
#            stock_tiles_hash=stock_tiles_hash,
#            status=MosaicImage.STATUS_PENDING,
#        )
#
#
#@periodic_task(crontab(minute='*/5'))
#def queue_mosaic_images_for_composition():
#    """
#    Search for any mosaic images that are pending or have errored during
#    composition.
#    """
#    mosaic_images_to_queue = MosaicImage.objects.filter(
#        Q(status=MosaicImage.STATUS_PENDING) |
#        Q(
#            status=MosaicImage.STATUS_COMPOSING,
#            updated_at__lte=MosaicImage.get_errored_datetime(),
#        )
#    ).distinct()
#
#    mosaic_image_pks = tuple(mosaic_images_to_queue.values_list('pk', flat=True))
#
#    with transaction.atomic():
#        mosaic_images_to_queue.select_for_update().update(
#            status=MosaicImage.STATUS_PENDING,
#            updated_at=timezone.now(),
#        )
#    for mosaic_image_pk in mosaic_image_pks:
#        compose_mosaic_image(mosaic_image_pk)


@db_task()
def compose_mosaic_image(mosaic_image_pk):
    with Timer() as timer:
        with transaction.atomic():
            lock_aquired = MosaicImage.objects.select_for_update().filter(
                pk=mosaic_image_pk,
                status=MosaicImage.STATUS_PENDING,
            ).update(
                status=MosaicImage.STATUS_COMPOSING,
                updated_at=timezone.now(),
            )

        if not lock_aquired:
            logger.warning(
                "Unable to aquire lock on MosaicImage: %s",
                mosaic_image_pk,
            )
            return

        mosaic_image = MosaicImage.objects.get(pk=mosaic_image_pk)
        mosaic_image.image.compose_mosaic(
            compose_tile_size=mosaic_image.tile_size,
            mosaic_image=mosaic_image,
        )
        mosaic_image.status = MosaicImage.STATUS_COMPLETE
        mosaic_image.save()
    logger.info(
        "Took %s to compose MosaicImage: %s for NormalizedSourceImage: %s",
        timer.elapsed,
        mosaic_image_pk,
        mosaic_image.image.pk,
    )
