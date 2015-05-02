from mozy.apps.mosaic.utils import (
    normalize_image_dimensions,
)


def test_dimension_normalization(square_image):
    result = normalize_image_dimensions(
        square_image,
        tile_size=250,
    )
    assert result.size == (500, 500)
