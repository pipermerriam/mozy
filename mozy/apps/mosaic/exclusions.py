from pybloom import ScalableBloomFilter


class StockTileExclusions(object):
    """
    Object that keeps track of which stock tiles have already been used.
    """
    def __init__(self, source_image):
        self.source_image = source_image
        self.bloom_filter = ScalableBloomFilter(
            initial_capacity=source_image.all_tiles.count(),
            error_rate=0.0001,  # 1 in 10,000
        )
        for existing_matche_id in source_image.all_tiles.values_list('stock_tile_match', flat=True):
            self.bloom_filter.add(existing_matche_id)

    def __contains__(self, key):
        if key in self.bloom_filter:
            return True
        elif self.source_image.all_tiles.filter(stock_tile_match_id=key).exists():
            self.bloom_filter.add(key)
            return True
        return False
