from PIL import Image

from mozy.apps.mosaic.utils import (
    convert_image_to_django_file,
)

from mozy.apps.core.utils import (
    uuid_filename,
)


def test_tiles_as_rows(models, square_image):
    source_image = models.SourceImage.objects.create()
    source_image.original.save(
        uuid_filename(),
        convert_image_to_django_file(square_image),
        save=True,
    )
    n_im = source_image.create_normalized_image()

    n_im.create_tiles()

    assert n_im.tiles.count() == 900
