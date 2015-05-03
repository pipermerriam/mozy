from mozy.apps.mosaic.normalization import (
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
