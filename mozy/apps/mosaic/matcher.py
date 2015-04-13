from django.conf import settings

from mozy.apps.mosaic.backends import get_mosaic_backend


def create_mosaic(mosaic_image):
    already_used_ids = set(mosaic_image.all_tiles.values_list('stock_tile_match', flat=True))

    matcher = get_mosaic_backend(settings.MOSAIC_BACKEND)(exclusions=already_used_ids)

    for tile in mosaic_image.all_tiles.filter(stock_tile_match__isnull=True):
        tile_data = tile.scipy_tile_data
        stock_id, match_similarity = matcher.find_tile_match(tile_data)

        tile.stock_tile_match_id = stock_id
        tile.stock_tile_match_difference = match_similarity
        tile.save()
        print "Matched tile:{0} with stock_image:{1} - {2}".format(
            tile.pk, stock_id, match_similarity,
        )
    mosaic_image.compose_mosaic()
    return mosaic_image
