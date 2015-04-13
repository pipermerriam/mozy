import django_tables2 as tables

from mozy.apps.mosaic.models import (
    NormalizedStockImage,
)


class StockImageTable(tables.Table):
    class Meta:
        model = NormalizedStockImage
        fields = (
            'id',
            'image',
            'tile_image',
        )
