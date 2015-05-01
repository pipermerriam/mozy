import pytest

from PIL import Image


def image_fixture_factory(path):
    @pytest.yield_fixture
    def the_fixture():
        with Image.open(path) as img:
            yield img
    return the_fixture


portrait_image_large = image_fixture_factory('tests/images/test-portrait-1200x1600.jpg')
portrait_image = image_fixture_factory('tests/images/test-portrait-450x600.jpg')

landscape_image_large = image_fixture_factory('tests/images/test-landscape-1600x1200.jpg')
landscape_image = image_fixture_factory('tests/images/test-landscape-600x450.jpg')

square_image = image_fixture_factory('tests/images/test-square-600x600.jpg')
tiny_image = image_fixture_factory('test/images/test-tiny-1x1.jpg')


@pytest.fixture()
def models(transactional_db):
    from django.apps import apps

    dict_ = {M._meta.object_name: M for M in apps.get_models()}

    return type(
        'models',
        (object,),
        dict_,
    )


@pytest.fixture()
def prime_dimensions_source_image(inmemorystorage, models):
    from django.core.files import File
    source_image = models.SourceImage()
    source_image.original.save(
        'tests/images/test-prime-dimensions-599x449.jpg',
        File(open('tests/images/test-prime-dimensions-599x449.jpg')),
        save=True
    )
    return source_image


@pytest.fixture(autouse=True)
def _inmemorystorage(settings):
    settings.STATICFILES_STORAGE = 'inmemorystorage.storage.InMemoryStorage'
    settings.DEFAULT_FILE_STORAGE = 'inmemorystorage.storage.InMemoryStorage'
    settings.INMEMORYSTORAGE_PERSIST = True


@pytest.fixture()
def inmemorystorage(_inmemorystorage):
    """
    Allows for use of the `InMemoryStorage` backend such that data persists
    between different instantiations of the storage backend.
    """
    from django.core.files.storage import default_storage
    return default_storage
