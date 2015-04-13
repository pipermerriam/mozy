import functools

from mozy.apps.mosaic.utils import (
    cast_image_data_to_scipy_array,
)
from mozy.apps.mosaic.models import (
    NormalizedStockImage,
)


def load_stock_data(tile_size):
    stock_data = []

    qs = NormalizedStockImage.objects.values_list('pk', 'tile_data')
    for stock_id, data in qs:
        stock_data.append(
            (
                cast_image_data_to_scipy_array(data),
                stock_id,
            )
        )
    return tuple(stock_data)


def measure_similarity(tile_data, stock_data):
    """
    Naive euclidean distance measure of the RGB tile data.
    """
    diff = tile_data - stock_data
    measure = sum(sum(sum(abs(diff))))
    return measure


def find_tile_match(tile_data, stock_data, exclusions):
    best_match = 1e12  # sufficiently large to not be a good match
    best_match_id = None

    for data, stock_id in stock_data:
        if stock_id in exclusions:
            continue

        similarity = measure_similarity(tile_data, data)

        if similarity < best_match:
            best_match = similarity
            best_match_id = stock_id

    exclusions.add(best_match_id)

    return best_match_id, best_match


def BruteForceTileMatcher(exclusions=None):
    if exclusions is None:
        exclusions = set()
    stock_data = load_stock_data(tile_size=20)

    return type(
        'BruteForceTileMatcher',
        (object,),
        {
            'exclusions': exclusions,
            'stock_data': stock_data,
            'find_tile_match': functools.partial(
                find_tile_match,
                stock_data=stock_data,
                exclusions=exclusions,
            ),
        },
    )()
