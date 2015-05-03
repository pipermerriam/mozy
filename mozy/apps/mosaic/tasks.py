import uuid
import logging

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


MATCH_BATCH_SIZE = excavator.env_int('MOSAIC_BATCH_SIZE', default=20)


@periodic_task(crontab(minute='*'))
def queue_source_image_tiles_for_matching():
    if not SourceImageTile.objects.unmatched().exists():
        return
    if SourceImageTile.objects.processing().exists():
        return

    logger.info("Queueing tiles for matching")
    for _ in range(MATCH_BATCH_SIZE):
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
        tiles = SourceImageTile.objects.unmatched().order_by(
            'updated_at',
        )[:MATCH_BATCH_SIZE]
        if not tiles:
            logger.info("No tiles to match")
            return
        for tile in tiles:
            # get lock
            with transaction.atomic():
                lock_aquired = SourceImageTile.objects.select_for_update(
                ).filter(
                    task_lock=tile.task_lock,
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
            return

    with Timer() as timer:
        matcher = get_mosaic_backend()(tile.main_image)

        match_data = matcher((
            (tile.pk, tile.numpy_tile_data),
        ))
        if not match_data:
            logger.warning("Could not find match for tile: %s", tile.pk)
            return

        _, stock_id, match_similarity = match_data[0]

        logger.info(
            "Matched SourceImageTile: %s with StockImage: %s with similarity %s",
            tile.pk, stock_id, match_similarity,
        )

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


@periodic_task(crontab(minute='*'))
def queue_mosaic_images_for_composition():
    """
    Search for any mosaic images that are pending or have errored during
    composition.
    """
    if not NormalizedSourceImage.objects.ready_for_mosaic().exists():
        return
    if NormalizedSourceImage.objects.composing().exists():
        return

    logger.info("Queueing source images for mosaic composition.")
    for _ in range(2):
        compose_mosaic_image()


@db_task()
def compose_mosaic_image(source_image_pk=None):
    if source_image_pk:
        # TODO. specified creation.
        pass
    else:
        source_image = NormalizedSourceImage.objects.ready_for_mosaic().first()
        if not source_image:
            return

    with transaction.atomic():
        lock_aquired = NormalizedSourceImage.objects.select_for_update(
        ).filter(
            task_lock=source_image.task_lock,
            pk=source_image.pk,
        ).update(
            task_lock=uuid.uuid4(),
            updated_at=timezone.now(),
        )

    if lock_aquired:
        logger.info(
            "Aquired lock on NormalizedSourceImage: %s",
            source_image.pk,
        )
    else:
        logger.warning(
            "Unable to aquire lock on NormalizedSourceImage: %s",
            source_image.pk,
        )
        return

    with Timer() as timer:
        mosaic_image = source_image.compose_mosaic()

    logger.info(
        "Took %s to compose MosaicImage: %s for NormalizedSourceImage: %s",
        timer.elapsed,
        mosaic_image.pk,
        source_image.pk,
    )
