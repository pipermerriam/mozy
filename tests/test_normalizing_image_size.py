from mozy.apps.mosaic.utils import (
    normalize_image_size,
    normalize_image_dimensions,
)


def test_size_normalization_on_large_portrait_image(portrait_image_large):
    result = normalize_image_size(
        portrait_image_large,
        max_width=600,
        max_height=600,
    )
    assert result.size == (450, 600)


def test_size_normalization_on_large_landscape_image(landscape_image_large):
    result = normalize_image_size(
        landscape_image_large,
        max_width=600,
        max_height=600,
    )
    assert result.size == (600, 450)


def test_size_normalization_on_image_within_range(landscape_image):
    initial_size = landscape_image.size
    result = normalize_image_size(
        landscape_image,
        max_width=1000,
        max_height=1000,
    )
    assert result.size == initial_size
#
#
#from hypothesis import given
#from hypothesis.specifiers import integers_in_range
#
#from PIL import Image
#
##
## Neat but slowwwww
#
#@given(integers_in_range(400, 800), integers_in_range(800, 800))
#def test_resizing(max_width, max_height):
#    img = Image.open('tests/images/test-portrait-1200x1600.jpg')
#    ratio = img.size[0] / img.size[1]
#
#    result = normalize_image_size(img, max_width=max_width, max_height=max_height)
#    res_ratio = result.size[0] / result.size[1]
#
#    diff = abs(res_ratio - ratio)
#    assert diff < 0.001
