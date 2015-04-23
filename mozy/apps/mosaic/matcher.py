import time

from django.db import transaction
from django.conf import settings

from mozy.apps.mosaic.models import NormalizedSourceImage
from mozy.apps.mosaic.backends import get_mosaic_backend


def create_mosaic(mosaic_image, compose_tile_size=None):
    already_used_ids = set(
        mosaic_image.all_tiles.values_list('stock_tile_match', flat=True)
    )

    matcher = get_mosaic_backend(settings.MOSAIC_BACKEND)(
        exclusions=already_used_ids,
        tile_size=mosaic_image.tile_size,
    )

    for tile in mosaic_image.all_tiles.filter(stock_tile_match__isnull=True):
        tile_data = tile.numpy_tile_data
        stock_id, match_similarity = matcher(tile_data)

        tile.stock_tile_match_id = stock_id
        tile.stock_tile_match_difference = match_similarity
        tile.save()
        print "Matched tile:{0} with stock_image:{1} - {2}".format(
            tile.pk, stock_id, match_similarity,
        )
    mosaic_image.compose_mosaic(compose_tile_size=compose_tile_size)
    return mosaic_image


def worker():
    """
    Work in progress.
    """
    while True:
        pending_work = NormalizedSourceImage.objects.filter(
            all_tiles__stock_tile_match__isnull=True,
        ).first()
        if pending_work:
            source_image_pk = pending_work.pk
            with transaction.atomic():
                source_image = NormalizedSourceImage.objects.select_for_update().get(
                    pk=source_image_pk,
                )
                create_mosaic(source_image)
        time.sleep(2)
