import functools
import itertools

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

from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
)
from mozy.apps.mosaic.models import (
    StockImageTile,
)


from contexttimer import Timer


#def load_stock_data(tile_size=20):
#    with Timer() as timer:
#        stock_data = []
#
#        qs = StockImageTile.objects.filter(
#            tile_size=tile_size,
#        ).values_list('stock_image', 'tile_data')
#        for stock_id, data in qs:
#            stock_data.append(
#                (
#                    cast_image_data_to_numpy_array(data),
#                    stock_id,
#                )
#            )
#    print "Stock loading took", timer.elapsed
#    return tuple(stock_data)
#
#
def load_stock_data(tile_size=20):
    with Timer() as timer:
        qs = StockImageTile.objects.filter(
            tile_size=tile_size,
        ).order_by('pk').values_list('stock_image', 'tile_data')
        rows = len(qs)
        stock_data = tuple((
            (cast_image_data_to_numpy_array(data), stock_id)
            for stock_id, data in slice for slice in qs[i: i + 1000] for i in range(0, rows, 1000)
        ))
    print "Stock loading took", timer.elapsed
    return stock_data


def reset_stock_data(tile_size=20):
    global STOCK_DATA
    STOCK_DATA = SimpleLazyObject(
        lambda: load_stock_data(tile_size=tile_size)
    )


STOCK_DATA = SimpleLazyObject(
    lambda: load_stock_data()
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
        convert_color(sRGBColor(r, g, b, is_upscaled=True), LabColor) for r, g, b in itertools.chain.from_iterable(pixel_data)
    ))


DELTA_E_MAX_DIFFERENCE = 50000


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


def find_tile_match(tile_data, stock_data, exclusions, match_threshold=0, compare_fn=measure_euclidean_similarity):
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


def BruteForceBestTileMatcher(tile_size, exclusions=None):
    if exclusions is None:
        exclusions = set()

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=exclusions,
    )


def BruteForceDeltaETileMatcher(tile_size, exclusions=None):
    if exclusions is None:
        exclusions = set()

    return functools.partial(
        find_tile_match,
        stock_data=STOCK_DATA,
        exclusions=exclusions,
        compare_fn=measure_delta_e_similarity,
    )


# Value is derived from mean + 2 standard deviations which should be within
# range for 95% of matches
# NOTE: This threshold is too high.  Needs to be lower somehow.
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
