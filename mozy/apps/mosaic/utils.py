from __future__ import division

import numpy

import StringIO

from django.conf import settings
from django.core.files.base import ContentFile


def compute_tile_boxes(size_x, size_y, tile_size):
    if size_x % tile_size or size_y % tile_size:
        raise ValueError("Image dimensions are not a multiple of tile size")
    return tuple([
        (x, y, x + tile_size, y + tile_size)
        for y in range(0, size_y, tile_size)
        for x in range(0, size_x, tile_size)
    ])


def decompose_an_image(image, tile_size=None):
    size_x, size_y = image.size
    if tile_size is None:
        tile_size = settings.MOSAIC_DEFAULT_TILE_SIZE

    return dict((
        (box, image.crop(box))
        for box
        in compute_tile_boxes(size_x=size_x, size_y=size_y, tile_size=tile_size)
    ))


def convert_image_to_django_file(image):
    image_file = StringIO.StringIO()
    image.save(image_file, format='PNG')
    image_file.seek(0)
    return ContentFile(image_file.getvalue())


def cast_image_data_to_numpy_array(image_data):
    return numpy.array([
        numpy.array([
            numpy.array(rgb) for rgb in row
        ]) for row in image_data
    ])


def cast_numpy_array_to_python(numpy_array):
    return [[[rgb for rgb in pixel] for pixel in row] for row in numpy_array]


def extract_pixel_data_from_image(im):
    x_size, y_size = im.size
    flat_pixel_data = tuple(im.getdata())
    pixel_data = tuple((
        tuple(flat_pixel_data[i:i + x_size]) for i in range(0, len(flat_pixel_data), x_size)
    ))
    if len(pixel_data) != y_size or not all(len(row) == x_size for row in pixel_data):
        raise ValueError("Something went wrong")
    return pixel_data
