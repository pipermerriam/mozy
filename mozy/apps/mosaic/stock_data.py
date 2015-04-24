import excavator

from django.conf import settings
from django.utils.module_loading import import_string

from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
)
from mozy.apps.mosaic.models import (
    StockImageTile,
)


def get_stock_data_backend(backend_class=None):
    if backend_class is None:
        backend_class = settings.MOSAIC_STOCK_DATA_BACKEND
    return import_string(backend_class)


class BaseStockDataBackend(object):
    """
    Base class which defines the interface a stock data backend must implement.
    """
    def __iter__(self):
        raise NotImplementedError("Subclasses must implement an iter method")


DB_CHUNK_SIZE = excavator.env_int('STOCK_DATA_CHUNK_SIZE', default=2000)


class InMemoryStockDataBackend(BaseStockDataBackend):
    """
    Fully loads the stock data into memory.
    """
    def __init__(self, chunk_size=None):
        if chunk_size is None:
            chunk_size = DB_CHUNK_SIZE
        self.chunk_size = chunk_size
        self._stock_data = []

    def __iter__(self):
        if isinstance(self._stock_data, tuple):
            return iter(self._stock_data)
        else:
            return self.load_stock_data()

    def load_stock_data(self):
        qs = StockImageTile.objects.filter(
            tile_size=20,
        ).order_by('pk').values_list('stock_image', 'tile_data')
        rows = qs.count()

        for i in range(0, rows, self.chunk_size):
            for stock_id, tile_data in qs[i:i + self.chunk_size]:
                np_tile_data = cast_image_data_to_numpy_array(tile_data)
                yield np_tile_data, stock_id
                self._stock_data.append(
                    (cast_image_data_to_numpy_array(tile_data), stock_id)
                )
        self._stock_data = tuple(self._stock_data)


class LowMemoryStockDataBackend(BaseStockDataBackend):
    def __init__(self, chunk_size=None):
        if chunk_size is None:
            chunk_size = DB_CHUNK_SIZE
        self.chunk_size = chunk_size

    def __iter__(self):
        qs = StockImageTile.objects.filter(
            tile_size=20,
        ).order_by('pk').values_list('stock_image', 'tile_data')
        rows = qs.count()

        for i in range(0, rows, self.chunk_size):
            for stock_id, tile_data in qs[i:i + self.chunk_size]:
                np_tile_data = cast_image_data_to_numpy_array(tile_data)
                yield np_tile_data, stock_id
