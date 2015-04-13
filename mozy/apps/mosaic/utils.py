from __future__ import division

import scipy

import StringIO

from django.conf import settings
from django.core.files.base import ContentFile


def normalize_image_size(image, max_width=None, max_height=None):
    if max_width is None:
        max_width = settings.MOSAIC_MAX_WIDTH
    if max_height is None:
        max_height = settings.MOSAIC_MAX_HEIGHT

    size_x, size_y = image.size

    scale_x = max_width / size_x if size_x > max_width else None
    scale_y = max_height / size_y if size_y > max_height else None
    # Handle larger images
    if scale_x or scale_y:
        if scale_x is not None and scale_x <= scale_y:
            image.thumbnail((
                max_width,
                max_height / scale_x,
            ))
        elif scale_y is not None:
            image.thumbnail((
                max_width / scale_y,
                max_height,
            ))
    return image


def normalize_image_dimensions(image, tile_size=None):
    if tile_size is None:
        tile_size = settings.MOSAIC_DEFAULT_TILE_SIZE

    size_x, size_y = image.size

    # Crop to multiple of tile_size
    if size_x % tile_size or size_y % tile_size:
        extra_x = size_x % tile_size
        extra_y = size_y % tile_size

        c_size_x = size_x - extra_x
        c_size_y = size_y - extra_y

        c_box = (
            int(extra_x / 2),
            int(extra_y / 2),
            int(extra_x / 2 + c_size_x),
            int(extra_y / 2 + c_size_y),
        )
        return image.crop(c_box)

    return image


def normalize_source_image(image, tile_size=None):
    """
    Takes a raw image that may be huge, or shaped funny, or something and
    forces it into a format that can be reasoned about.

    - MIN_WIDTH < Width < MAX_WIDTH
    - MIN_HEIGHT < Height < MAX_HEIGHT
    - Width is multiple of tile_size
    - Height is multiple of tile_size
    """
    o_size_x, o_size_y = image.size

    # Handle too small images
    if o_size_x < settings.MOSAIC_MIN_WIDTH or o_size_y < settings.MOSAIC_MIN_HEIGHT:
        raise ValueError("Image is too small.  Must be at least {width}x{height}".format(
            width=settings.MOSAIC_MIN_WIDTH,
            height=settings.MOSAIC_MIN_HEIGHT,
        ))

    # Handle larger images
    downsized_image = normalize_image_size(image)

    # Crop to multiple of tile_size
    cropped_and_downsized_image = normalize_image_dimensions(
        downsized_image, tile_size=tile_size,
    )

    return cropped_and_downsized_image


def convert_image_to_square(image):
    size_x, size_y = image.size

    if size_x > size_y:
        return image.crop((
            int((size_x - size_y) / 2),
            0,
            int((size_x - size_y) / 2 + size_y),
            size_y,
        ))
    elif size_y > size_x:
        return image.crop((
            0,
            0,
            size_x,
            size_x,
        ))
    else:
        return image


def normalize_stock_image(image, tile_size=None):
    o_size_x, o_size_y = image.size

    # Handle too small images
    if o_size_x < settings.MOSAIC_MIN_WIDTH or o_size_y < settings.MOSAIC_MIN_HEIGHT:
        raise ValueError("Image is too small.  Must be at least {width}x{height}".format(
            width=settings.MOSAIC_MIN_WIDTH,
            height=settings.MOSAIC_MIN_HEIGHT,
        ))

    # Handle larger images
    downsized_image = normalize_image_size(image)

    # Crop to multiple of tile_size
    cropped_and_downsized_image = normalize_image_dimensions(downsized_image)

    # Now crop to be square
    cropped_and_downsized_and_squared_image = convert_image_to_square(
        cropped_and_downsized_image,
    )

    return cropped_and_downsized_and_squared_image


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


def cast_image_data_to_scipy_array(image_data):
    return scipy.array([
        scipy.array([
            scipy.array(rgb) for rgb in row
        ]) for row in image_data
    ])


def cast_scipy_array_to_python(scipy_array):
    return [[[rgb for rgb in pixel] for pixel in row] for row in scipy_array]
