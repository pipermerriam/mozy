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


# https://docs.djangoproject.com/en/1.8/ref/models/fields/#positiveintegerfield
# max for models.PositiveSmallIntegerField
SIMILARITY_MAX = 2147483647


def normalize_measure(value, maximum):
    if value > maximum:
        raise ValueError(
            "Cannot normalize a value above the maximum. {0} > {1}".format(
                value, maximum,
            )
        )
    return int(value * SIMILARITY_MAX / maximum)


# 255 * 3 colors * 20 pixels * 20 pixels
MAX_EUCLIDEAN_DIFFERENCE = 255 * 3 * 20 * 20  # 306000


def measure_diff_similarity(tile_data, stock_data):
    """
    Naive absolute difference measure of the RGB tile data.
    """
    diff = tile_data - stock_data
    measure = sum(sum(sum(abs(diff))))
    n_measure = normalize_measure(measure, MAX_EUCLIDEAN_DIFFERENCE)
    return n_measure


#
#  DELTA-E Image Similarity
#
#  This method is about 10,000 times slower than the diff method.
#
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
