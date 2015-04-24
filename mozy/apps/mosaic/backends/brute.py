import functools
import excavator

from mozy.apps.mosaic.stock_data import (
    get_stock_data_backend,
)
from mozy.apps.mosaic.similarity import (
    SIMILARITY_MAX,
    measure_diff_similarity,
)
from mozy.apps.mosaic.exclusions import (
    StockTileExclusions,
)


def find_tile_match(tile_data, stock_data, exclusions, match_threshold=0,
                    compare_fn=measure_diff_similarity):
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


def BruteForceBestTileMatcher(source_image):
    # Used to determine if a tile has already been used.
    exclusions = StockTileExclusions(source_image)
    # Source for the stock data that will be matched against.
    stock_data = get_stock_data_backend()()
    # If set, determines when a match is good enough as an early exit condition
    # when iterating over stock data.
    match_threshold = excavator.env_int(
        'BRUTE_FORCE_GOOD_ENOUGH_THRESHOLD', default=0,
    )

    return functools.partial(
        find_tile_match,
        stock_data=stock_data,
        exclusions=exclusions,
        match_threshold=match_threshold,
    )
