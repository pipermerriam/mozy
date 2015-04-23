import functools
import itertools

from pybloom import BloomFilter

from colormath.color_diff import (
    delta_e_cie2000,
)
from colormath.color_objects import (
    sRGBColor,
    LabColor,
)
from colormath.color_conversions import (
    convert_color,
)

from django.utils.functional import SimpleLazyObject
from django.conf import settings

from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
)
from mozy.apps.mosaic.models import (
    StockImageTile,
)


def load_stock_data(tile_size=20):
    qs = StockImageTile.objects.filter(
        tile_size=tile_size,
    ).order_by('pk').values_list('stock_image', 'tile_data')
    rows = qs.count()
    stock_data = tuple((
        (cast_image_data_to_numpy_array(tile_data), stock_id)
        for stock_id, tile_data
        in itertools.chain.from_iterable(qs[i:i + 500] for i in range(0, rows, 500))
    ))
    return stock_data


STOCK_DATA = SimpleLazyObject(load_stock_data)


def reset_stock_data(tile_size=20):
    global STOCK_DATA  # NOQA
    STOCK_DATA = SimpleLazyObject(
        functools.partial(load_stock_data, tile_size)
    )


# https://docs.djangoproject.com/en/1.8/ref/models/fields/#positiveintegerfield
# max for models.PositiveSmallIntegerField
SIMILARITY_MAX = 2147483647


def normalize_measure(value, maximum):
    if value > maximum:
        raise ValueError("Cannot normalize a value above the maximum")
    return int(value * SIMILARITY_MAX / maximum)


# 255 * 3 colors * 20 pixels * 20 pixels
MAX_EUCLIDEAN_DIFFERENCE = 255 * 3 * 20 * 20  # 306000


def measure_euclidean_similarity(tile_data, stock_data):
    """
    Naive euclidean distance measure of the RGB tile data.
    """
    diff = tile_data - stock_data
    measure = sum(sum(sum(abs(diff))))
    n_measure = normalize_measure(measure, MAX_EUCLIDEAN_DIFFERENCE)
    return n_measure


def convert_pixel_data_to_lab_colors(pixel_data):
    return tuple((
        convert_color(sRGBColor(r, g, b, is_upscaled=True), LabColor)
        for r, g, b
        in itertools.chain.from_iterable(pixel_data)
    ))


DELTA_E_MAX_DIFFERENCE = 40000


def measure_delta_e_similarity(tile_data, stock_data):
    tile_data_colors = convert_pixel_data_to_lab_colors(tile_data)
    stock_data_colors = convert_pixel_data_to_lab_colors(stock_data)
    differences = tuple((
        delta_e_cie2000(td_color, sd_color)
        for td_color, sd_color
        in zip(tile_data_colors, stock_data_colors)
    ))
    measure = sum(differences)
    n_measure = normalize_measure(measure, DELTA_E_MAX_DIFFERENCE)
    return n_measure


def find_tile_match(tile_data, stock_data, exclusions, match_threshold=0,
                    compare_fn=measure_euclidean_similarity):
    best_match = SIMILARITY_MAX
    best_match_id = None

    for data, stock_id in stock_data:
        if stock_id in exclusions:
            continue

        similarity = compare_fn(tile_data, data)

        if similarity < best_match:
            best_match = similarity
            best_match_id = stock_id

        if similarity <= match_threshold:
            break

    exclusions.add(best_match_id)

    return best_match_id, best_match


def get_bloom_filter(exclusions):
    bloom_filter = BloomFilter(
        capacity=settings.MOSAIC_MAX_WIDTH * settings.MOSAIC_MAX_HEIGHT / 400,
        error_rate=0.0001,
    )
    for exclusion in exclusions or []:
        bloom_filter.add(exclusion)
    return bloom_filter


def BruteForceBestTileMatcher(tile_size, exclusions=None):
    bloom_filter = get_bloom_filter(exclusions)

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=bloom_filter,
    )


def BruteForceDeltaETileMatcher(tile_size, exclusions=None):
    bloom_filter = get_bloom_filter(exclusions)

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=bloom_filter,
        compare_fn=measure_delta_e_similarity,
    )


# Value is derived from mean + 2 standard deviations which should be within
# range for 95% of matches
# NOTE: This threshold is too high.  Needs to be lower somehow.
GOOD_ENOUGH_THRESHOLD = 47396


def BruteForceGoodEnoughTileMatcher(tile_size, exclusions=None):
    bloom_filter = get_bloom_filter(exclusions)

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=bloom_filter,
        match_threshold=GOOD_ENOUGH_THRESHOLD,
    )
