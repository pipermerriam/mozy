import pytest


@pytest.mark.parametrize(
    'tile_kwargs,tile_size,box',
    (
        # 20
        ({'x_coord': 0, 'y_coord': 0}, 20, (0, 0, 20, 20)),
        ({'x_coord': 1, 'y_coord': 0}, 20, (20, 0, 40, 20)),
        ({'x_coord': 0, 'y_coord': 1}, 20, (0, 20, 20, 40)),
        ({'x_coord': 1, 'y_coord': 1}, 20, (20, 20, 40, 40)),
        ({'x_coord': 4, 'y_coord': 5}, 20, (80, 100, 100, 120)),
        # 30
        ({'x_coord': 0, 'y_coord': 0}, 30, (0, 0, 30, 30)),
        ({'x_coord': 1, 'y_coord': 0}, 30, (30, 0, 60, 30)),
        ({'x_coord': 0, 'y_coord': 1}, 30, (0, 30, 30, 60)),
        ({'x_coord': 1, 'y_coord': 1}, 30, (30, 30, 60, 60)),
        ({'x_coord': 4, 'y_coord': 5}, 30, (120, 150, 150, 180)),
    )
)
def test_get_image_box(models, tile_kwargs, tile_size, box):
    tile = models.SourceImageTile(**tile_kwargs)
    actual = tile.get_image_box(tile_size)
    assert actual == box
