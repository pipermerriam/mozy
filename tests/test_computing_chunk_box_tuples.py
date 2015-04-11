from mozy.apps.mosaic.utils import (
    compute_tile_boxes,
)


def test_check_boxes_for_2_by_3():
    boxes = compute_tile_boxes(size_x=20, size_y=30, tile_size=10)
    assert len(boxes) == 6
    assert boxes[0] == (0, 0, 10, 10)
    assert boxes[1] == (10, 0, 20, 10)
    assert boxes[2] == (0, 10, 10, 20)
    assert boxes[3] == (10, 10, 20, 20)
    assert boxes[4] == (0, 20, 10, 30)
    assert boxes[5] == (10, 20, 20, 30)
