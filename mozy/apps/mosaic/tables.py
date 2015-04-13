import django_tables2 as tables
from django_tables2 import (
    A,
)

from mozy.apps.core.tables import (
    BootstrapTable,
)
from mozy.apps.mosaic.models import (
    SourceImage,
    NormalizedStockImage,
)


class SourceImageTable(BootstrapTable):
    original = tables.LinkColumn(
        'sourceimage-detail',
        kwargs={'pk': A('pk')},
        verbose_name='Image',
        orderable=False,
    )

    class Meta(BootstrapTable.Meta):
        model = SourceImage
        fields = (
            'id',
            'original',
        )


class StockImageTable(BootstrapTable):
    class Meta(BootstrapTable.Meta):
        model = NormalizedStockImage
        fields = (
            'id',
            'image',
            'tile_image',
        )
