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
