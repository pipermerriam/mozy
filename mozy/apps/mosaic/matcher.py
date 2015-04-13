import functools

from django.conf import settings

from mozy.apps.mosaic.backends import get_mosaic_backend
from mozy.apps.mosaic.models import MosaicTile

from multiprocessing import Pool


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


def _callback(tile_id, result):
    stock_id, match_similarity = result

    tile = MosaicTile.objects.get(pk=tile_id)
    tile.stock_tile_match_id = stock_id
    tile.stock_tile_match_difference = match_similarity
    print "Matched tile:{0} with stock_image:{1} - {2}".format(
        tile.pk, stock_id, match_similarity,
    )
    tile.save()


def create_mosaic_async(mosaic_image):
    """
    Why is this slower?
    """
    already_used_ids = set(mosaic_image.all_tiles.values_list('stock_tile_match', flat=True))

    pool = Pool(processes=4)

    matcher = get_mosaic_backend(settings.MOSAIC_BACKEND)(exclusions=already_used_ids)

    for tile in mosaic_image.all_tiles.filter(stock_tile_match__isnull=True):
        tile_data = tile.scipy_tile_data

        pool.apply_async(
            matcher.find_tile_match,
            (tile_data,),
            callback=functools.partial(_callback, tile.pk),
        )

    pool.close()
    pool.join()

    mosaic_image.compose_mosaic()
    return mosaic_image
