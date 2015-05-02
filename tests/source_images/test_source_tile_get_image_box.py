import pytest


@pytest.mark.parametrize(
    'tile_kwargs,tile_size,box',
    (
        # 20
        ({'upper_left_x': 0, 'upper_left_y': 0}, 20, (0, 0, 20, 20)),
        ({'upper_left_x': 20, 'upper_left_y': 0}, 20, (20, 0, 40, 20)),
        ({'upper_left_x': 0, 'upper_left_y': 20}, 20, (0, 20, 20, 40)),
        ({'upper_left_x': 20, 'upper_left_y': 20}, 20, (20, 20, 40, 40)),
        ({'upper_left_x': 80, 'upper_left_y': 100}, 20, (80, 100, 100, 120)),
        # 30
        ({'upper_left_x': 0, 'upper_left_y': 0}, 30, (0, 0, 30, 30)),
        ({'upper_left_x': 20, 'upper_left_y': 0}, 30, (30, 0, 60, 30)),
        ({'upper_left_x': 0, 'upper_left_y': 20}, 30, (0, 30, 30, 60)),
        ({'upper_left_x': 20, 'upper_left_y': 20}, 30, (30, 30, 60, 60)),
        ({'upper_left_x': 80, 'upper_left_y': 100}, 30, (120, 150, 150, 180)),
    )
)
def test_get_image_box(models, tile_kwargs, tile_size, box):
    tile = models.SourceImageTile(**tile_kwargs)
    actual = tile.get_image_box(tile_size)
    assert actual == box
