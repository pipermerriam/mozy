import collections
import itertools
import operator
import functools

import excavator

from mozy.apps.mosaic.models import (
    StockImageTile,
    Generation,
)
from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
)
from mozy.apps.mosaic.similarity import (
    SIMILARITY_MAX,
    measure_diff_similarity,
)
from mozy.apps.mosaic.exclusions import (
    StockTileExclusions,
)
from mozy.apps.mosaic.stock_data import (
    InMemoryGroupDataBackend,
)


def find_k_means_groups(tile_data_array, group_data,
                        compare_fn=measure_diff_similarity):
    best_matches = collections.defaultdict(lambda: SIMILARITY_MAX)
    best_match_ids = {}

    for data, group_id in group_data:
        for tile_id, tile_data in tile_data_array:
            similarity = compare_fn(tile_data, data)
            best_match = best_matches[tile_id]

            if similarity < best_match:
                best_matches[tile_id] = similarity
                best_match_ids[tile_id] = group_id

    return tuple((
        (tile_id, group_id, best_matches[tile_id])
        for tile_id, group_id in best_match_ids.items()
    ))


def find_best_group_tiles(tile_data_array, group_stock_data, exclusions,
                          compare_fn=measure_diff_similarity):
    best_matches = collections.defaultdict(lambda: SIMILARITY_MAX)
    best_match_ids = {}

    for data, stock_id in group_stock_data:
        for tile_id, tile_data in tile_data_array:
            if (tile_id, stock_id) in exclusions:
                continue

            similarity = compare_fn(tile_data, data)
            best_match = best_matches[tile_id]

            if similarity < best_match:
                best_matches[tile_id] = similarity
                best_match_ids[tile_id] = stock_id

    for tile_id, stock_id in best_match_ids.items():
        exclusions.add((tile_id, stock_id))

    return tuple((
        (tile_id, stock_id, best_matches[tile_id])
        for tile_id, stock_id in best_match_ids.items()
    ))


def find_tile_matches(tile_data_array, group_data, exclusions,
                      compare_fn=measure_diff_similarity):

    group_match_data = find_k_means_groups(
        tile_data_array,
        group_data=group_data,
        compare_fn=compare_fn,
    )
    tile_data_lookup = dict(tile_data_array)
    groupby_key = operator.itemgetter(1)  # group_id
    grouped_by_group_match_data = itertools.groupby(group_match_data, groupby_key)

    tile_match_data_array = []

    for group_id, match_data in grouped_by_group_match_data:
        tile_ids = zip(*match_data)[0]
        stock_tile_qs = StockImageTile.objects.filter(
            groups__id=group_id
        ).values_list('stock_image', 'tile_data').distinct()
        group_stock_data = tuple((
            (cast_image_data_to_numpy_array(tile_data), stock_id)
            for stock_id, tile_data
            in stock_tile_qs
        ))
        tile_match_data = find_best_group_tiles(
            tuple((
                (tile_id, tile_data_lookup[tile_id]) for tile_id in tile_ids
            )),
            group_stock_data,
            exclusions,
            compare_fn=compare_fn,
        )
        tile_match_data_array.append(tile_match_data)

    return zip(*zip(*itertools.chain.from_iterable(tile_match_data_array)))


K_MEANS_GENERATION_ID = excavator.env_int('K_MEANS_GENERATION_ID', 37)


def KMeansTileMatcher(source_image):
    # Used to determine if a tile has already been used.
    exclusions = StockTileExclusions(source_image)
    # Source for the stock data that will be matched against.
    group_data = InMemoryGroupDataBackend(
        generation=Generation.objects.get(pk=K_MEANS_GENERATION_ID)
    )

    return functools.partial(
        find_tile_matches,
        group_data=group_data,
        exclusions=exclusions,
        compare_fn=measure_diff_similarity,
    )
