import logging

from django.conf import settings

from mozy.apps.mosaic.backends import get_mosaic_backend


logger = logging.getLogger(__file__)


def create_mosaic(source_image, compose_tile_size=None):
    already_used_ids = set(
        source_image.all_tiles.values_list('stock_tile_match', flat=True)
    )

    matcher = get_mosaic_backend(settings.MOSAIC_BACKEND)(
        exclusions=already_used_ids,
        tile_size=source_image.tile_size,
    )

    tile_qs = source_image.all_tiles.filter(stock_tile_match__isnull=True)

    for tile in tile_qs:
        tile_data = tile.numpy_tile_data
        stock_id, match_similarity = matcher(tile_data)

        tile.stock_tile_match_id = stock_id
        tile.stock_tile_match_difference = match_similarity
        tile.save()
        logger.info(
            "Matched tile:%s with stock_image:%s - %s",
            tile.pk, stock_id, match_similarity,
        )

    mosaic_image = source_image.mosaic_images.filter(tile_size=compose_tile_size).first()
    if not mosaic_image:
        logger.info("Composing Mosaic image for source_image:%s", source_image.pk)
        mosaic_image = source_image.compose_mosaic(compose_tile_size=compose_tile_size)
    return mosaic_image
