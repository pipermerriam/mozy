def test_tiles_as_rows(models):
    n_im = models.NormalizedSourceImage.objects.create(
        source_image=models.SourceImage.objects.create(),
    )
    # 3 rows, 2 columns
    # ROW #1
    tile_0_0 = n_im.tiles.create(x_coord=0, y_coord=0, tile_data=[[[1]]])
    tile_0_1 = n_im.tiles.create(x_coord=1, y_coord=0, tile_data=[[[1]]])
    # ROW #2
    tile_1_0 = n_im.tiles.create(x_coord=0, y_coord=1, tile_data=[[[1]]])
    tile_1_1 = n_im.tiles.create(x_coord=1, y_coord=1, tile_data=[[[1]]])
    # ROW #3
    tile_2_0 = n_im.tiles.create(x_coord=0, y_coord=2, tile_data=[[[1]]])
    tile_2_1 = n_im.tiles.create(x_coord=1, y_coord=2, tile_data=[[[1]]])

    tiles_as_rows = n_im.tiles_as_rows()

    r1, r2, r3 = tiles_as_rows
    assert r1 == (tile_0_0, tile_0_1)
    assert r2 == (tile_1_0, tile_1_1)
    assert r3 == (tile_2_0, tile_2_1)
