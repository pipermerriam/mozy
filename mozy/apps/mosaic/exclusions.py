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
        existing_matches = source_image.all_tiles.values_list('pk', 'stock_tile_match')
        for tile_id, existing_match_id in existing_matches:
            self.bloom_filter.add((tile_id, existing_match_id))

    def __contains__(self, key):
        if key in self.bloom_filter:
            return True
        elif self.source_image.all_tiles.filter(stock_tile_match_id=key[1]).exists():
            self.add(key)
            return True
        return False

    def add(self, key):
        self.bloom_filter.add(key)


class DummyExclusions(object):
    """
    object which always returns false to exclusions checks.
    """
    def __contains__(self, key):
        return False

    def add(self, key):
        pass
