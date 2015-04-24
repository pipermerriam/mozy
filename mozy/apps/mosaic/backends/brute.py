import functools
import excavator
import collections

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


def find_tile_matches(tile_data_array, stock_data, exclusions, match_threshold=0,
                      compare_fn=measure_diff_similarity):
    best_matches = collections.defaultdict(lambda: SIMILARITY_MAX)
    best_match_ids = {}
    found_matches = set()

    for data, stock_id in stock_data:
        for tile_id, tile_data in tile_data_array:
            if tile_id in found_matches:
                continue
            if (tile_id, stock_id) in exclusions:
                continue

            similarity = compare_fn(tile_data, data)
            best_match = best_matches[tile_id]

            if similarity < best_match:
                best_matches[tile_id] = similarity
                best_match_ids[tile_id] = stock_id

            if similarity <= match_threshold:
                found_matches.add(tile_id)

    for tile_id, stock_id in best_match_ids.items():
        exclusions.add((tile_id, stock_id))

    return tuple((
        (tile_id, stock_id, best_matches[tile_id])
        for tile_id, stock_id in best_match_ids.items()
    ))


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
        find_tile_matches,
        stock_data=stock_data,
        exclusions=exclusions,
        match_threshold=match_threshold,
        compare_fn=measure_diff_similarity,
    )
