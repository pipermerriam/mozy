from mozy.apps.core.tables import (
    BootstrapTable,
)
from mozy.apps.mosaic.models import (
    NormalizedStockImage,
)


class StockImageTable(BootstrapTable):
    class Meta(BootstrapTable.Meta):
        model = NormalizedStockImage
        fields = (
            'id',
            'image',
            'tile_image',
        )
