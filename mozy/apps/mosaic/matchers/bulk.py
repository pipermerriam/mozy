import logging

from django.db.models import Q
from django.db import transaction

from mozy.apps.mosaic.backends import (
    get_mosaic_backend,
)
from mozy.apps.mosaic.models import (
    SourceImageTile,
)
from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
)


logger = logging.getLogger(__file__)


def create_mosaic(source_image, compose_tile_size=None):
    """
    A synchronous function useful for long running mosiac image generation.
    """
    matcher = get_mosaic_backend()(source_image)

    tile_qs = source_image.all_tiles.filter(
        stock_tile_match__isnull=True,
    ).values_list('pk', 'tile_data')

    for tile_pk, tile_data in tile_qs:
        stock_id, match_similarity = matcher(
            tuple([
                (tile_pk, cast_image_data_to_numpy_array(tile_data))
            ]),
        )

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

    mosaic_image = source_image.mosaic_images.filter(tile_size=compose_tile_size).first()
    if not mosaic_image:
        logger.info("Composing Mosaic image for source_image:%s", source_image.pk)
        mosaic_image = source_image.compose_mosaic(compose_tile_size=compose_tile_size)
    return mosaic_image
