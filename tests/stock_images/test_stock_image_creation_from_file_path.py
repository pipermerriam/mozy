import pytest

from mozy.apps.mosaic.models import (
    StockImage,
)


@pytest.mark.django_db
def test_stock_image_create_from_file_path(square_image, inmemorystorage):
    stock_image = StockImage.create_from_filepath(square_image.fp.name)
    assert stock_image.original.width == square_image.size[0]
    assert stock_image.original.height == square_image.size[1]
