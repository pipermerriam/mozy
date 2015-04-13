import functools

from scipy.misc import imread

from mozy.apps.mosaic.models import (
    NormalizedStockImage,
    MosaicTile,
)


def file_to_normalized_image_data(fp):
    data = imread(fp, flatten=True)
    # greyscale is probably wrong
    #greyscale_data = scipy.inner(data, [299, 587, 114]) / 1000.0
    #normalized_data = (data - data.mean()) / data.std()

    #return normalized_data
    return data


_stock_data = []


def load_stock_data(tile_size):
    global _stock_data
    if not _stock_data:
        for im in NormalizedStockImage.objects.filter(tile_size=tile_size):
            with im.tile_image.file as fp:
                _stock_data.append(
                    (file_to_normalized_image_data(fp), im.pk)
                )
    return _stock_data


def im_data_cmp_key(target_data, data):
    diff = target_data - data[0]
    measure = sum(sum(abs(diff)))
    return measure


def brute_force_find_tile_match(target_im_data, exclusions=None):
    if exclusions is None:
        exclusions = []
    haystack_image_data = load_stock_data(tile_size=20)
    sorted_data = sorted(
        haystack_image_data,
        key=functools.partial(im_data_cmp_key, target_im_data),
    )
    return sorted_data[0][1]


def create_mosaic(mosaic_image):
    already_used_ids = set(mosaic_image.all_tiles.values_list('stock_tile_match', flat=True))
    global _stock_data
    for tile in mosaic_image.all_tiles.filter(stock_tile_match__isnull=True):
        with tile.tile_image.file as fp:
            tile_im_data = file_to_normalized_image_data(fp)
        tile.stock_tile_match_id = brute_force_find_tile_match(tile_im_data)
        tile.save()
        already_used_ids.add(tile.stock_tile_match_id)
        _stock_data = [v for v in _stock_data if v[1] not in already_used_ids]
        print "Matched tile:{0} with stock_image:{1}".format(tile.pk, tile.stock_tile_match_id)
    mosaic_image.compose_mosaic()
    return mosaic_image.mosaic.path
