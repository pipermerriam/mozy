import uuid
import logging

from contexttimer import Timer

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
    cast_image_data_to_numpy_array,
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

    with Timer() as timer:
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
    logger.info(
        "Took %s to create source image tiles for NormalizedSourceImage: %s",
        timer.elapsed,
        source_image_pk,
    )

    if not source_image.mosaic_images.exists():
        queue_source_image_tile_tasks(source_image_pk)


MATCH_BATCH_SIZE = 100


@db_task()
def queue_source_image_tile_tasks(source_image_pk):
    """
    Queues tasks to match the source image tiles with stock image tiles.
    """
    source_image = NormalizedSourceImage.objects.get(pk=source_image_pk)
    tile_qs = source_image.all_tiles.order_by('pk').values_list('pk', flat=True)
    for i in range(0, tile_qs.count(), MATCH_BATCH_SIZE):
        tile_pks = tuple(tile_qs[i:i + MATCH_BATCH_SIZE])
        match_souce_image_tiles(tile_pks)


@db_task()
def match_souce_image_tiles(source_image_tile_pks):
    with Timer() as timer:
        source_image = NormalizedSourceImage.objects.get(all_tiles__pk=source_image_tile_pks[0])

        matcher = get_mosaic_backend()(source_image)

        tile_data_array = tuple((
            (tile_pk, cast_image_data_to_numpy_array(tile_data))
            for tile_pk, tile_data
            in SourceImageTile.objects.filter(pk__in=source_image_tile_pks).values_list(
                'pk', 'tile_data',
            )
        ))

        match_data = matcher(tile_data_array)

        for tile_pk, stock_id, match_similarity in match_data:
            with transaction.atomic():
                SourceImageTile.objects.select_for_update().filter(
                    (
                        Q(stock_tile_match_difference__isnull=True) |
                        Q(stock_tile_match_difference__lt=match_similarity)
                    ),
                    Q(pk=tile_pk),
                ).update(
                    stock_tile_match_id=stock_id,
                    stock_tile_match_difference=match_similarity,
                )
            logger.info(
                "Matched tile:%s with stock_image:%s - %s",
                tile_pk, stock_id, match_similarity,
            )
    logger.info(
        "Took %s to compose match %s tiles for NormalizedSourceImage: %s",
        timer.elapsed,
        len(source_image_tile_pks),
        source_image.pk,
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


@periodic_task(crontab(minute='*/5'))
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
            logger.error("Unable to aquire lock on MosaicImage: %s", mosaic_image_pk)
            return

        mosaic_image = MosaicImage.objects.get(pk=mosaic_image_pk)
        mosaic_image.image.compose_mosaic(
            compose_tile_size=mosaic_image.tile_size,
            mosaic_image=mosaic_image,
        )
    logger.info(
        "Took %s to compose MosaicImage: %s for NormalizedSourceImage: %s",
        timer.elapsed,
        mosaic_image_pk,
        mosaic_image.image.pk,
    )
