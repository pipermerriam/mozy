import pytest

from mozy.apps.mosaic.models import (
    StockImage,
    NormalizedStockImage,
)


@pytest.mark.django_db
def test_normalized_stock_image_creation(square_image, inmemorystorage):
    stock_image = StockImage.create_from_filepath(square_image.fp.name)
    norm_image = NormalizedStockImage.create_from_stock_image(stock_image)

    assert norm_image.image.width % norm_image.tile_size == 0
    assert norm_image.image.height % norm_image.tile_size == 0

    assert norm_image.tile_image.width % norm_image.tile_size == 0
    assert norm_image.tile_image.width == norm_image.tile_image.width
