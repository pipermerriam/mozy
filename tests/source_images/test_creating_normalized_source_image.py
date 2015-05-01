def test_create_normalized_image_method(prime_dimensions_source_image, inmemorystorage):
    normalized_source_image = prime_dimensions_source_image.create_normalized_image()
    assert inmemorystorage.exists(normalized_source_image.image.name)
    assert normalized_source_image.image.width % 20 == 0
    assert normalized_source_image.image.height % 20 == 0
