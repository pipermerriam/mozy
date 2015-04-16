import functools

from django.utils.functional import SimpleLazyObject

from mozy.apps.mosaic.utils import (
    cast_image_data_to_scipy_array,
)
from mozy.apps.mosaic.models import (
    StockImageTile,
)


def load_stock_data(tile_size):
    stock_data = []

    qs = StockImageTile.objects.filter(
        tile_size=tile_size,
    ).values_list('stock_image', 'tile_data')
    for stock_id, data in qs:
        stock_data.append(
            (
                cast_image_data_to_scipy_array(data),
                stock_id,
            )
        )
    return tuple(stock_data)


def reset_stock_data():
    global STOCK_DATA
    STOCK_DATA = SimpleLazyObject(
        lambda: load_stock_data(tile_size=tile_size)
    )


STOCK_DATA = SimpleLazyObject(
    lambda: load_stock_data(tile_size=tile_size)
)


def measure_similarity(tile_data, stock_data):
    """
    Naive euclidean distance measure of the RGB tile data.
    """
    diff = tile_data - stock_data
    measure = sum(sum(sum(abs(diff))))
    return measure


def find_tile_match(tile_data, stock_data, exclusions, match_threshold=None):
    # 255 * 3 colors * 20 pixels * 20 pixels
    best_match = 255 * 3 * 20 * 20  # 306000
    best_match_id = None

    for data, stock_id in stock_data:
        if stock_id in exclusions:
            continue

        similarity = measure_similarity(tile_data, data)

        if similarity < best_match:
            best_match = similarity
            best_match_id = stock_id

        if match_threshold and similarity <= match_threshold:
            break

    exclusions.add(best_match_id)

    return best_match_id, best_match


def BruteForceBestTileMatcher(tile_size, exclusions=None):
    if exclusions is None:
        exclusions = set()

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=exclusions,
    )


# Value is derived from mean + 2 standard deviations which should be within
# range for 95% of matches
GOOD_ENOUGH_THRESHOLD = 47396


def BruteForceGoodEnoughTileMatcher(tile_size, exclusions=None):
    if exclusions is None:
        exclusions = set()

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=exclusions,
        match_threshold=GOOD_ENOUGH_THRESHOLD,
    )
