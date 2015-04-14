from django.apps import AppConfig
from django import dispatch
from django.db.models.signals import (
    post_save,
)


class MosaicConfig(AppConfig):
    name = 'mozy.apps.mosaic'
    label = 'mosaic'
    verbose_name = 'Mosaic'

    def ready(self):
        # Signals
        from mozy.apps.mosaic.receivers import (
            create_mosaic_tiles,
            create_stock_tiles,
        )
        dispatch.receiver(post_save, sender='mosaic.MosaicImage')(
            create_mosaic_tiles,
        )
        dispatch.receiver(post_save, sender='mosaic.NormalizedStockImage')(
            create_stock_tiles,
        )
