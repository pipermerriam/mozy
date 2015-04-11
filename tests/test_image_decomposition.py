from mozy.apps.mosaic.utils import (
    decompose_an_image,
)


def test_image_decomposition(landscape_image):
    tiles = decompose_an_image(landscape_image, tile_size=150)
    assert len(tiles) == 12
    assert all(tile.size == (150, 150) for tile in tiles.values())
