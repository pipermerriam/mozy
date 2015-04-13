import itertools
import os
import operator
import uuid
import hashlib

from PIL import Image

from django.contrib.postgres.fields import ArrayField
from django.db import (
    models,
    transaction,
)

from mozy.apps.core.utils import generic_upload_to
from mozy.apps.core.models import Timestampable

from mozy.apps.mosaic.utils import (
    cast_image_data_to_scipy_array,
    convert_image_to_django_file,
    normalize_source_image,
    normalize_stock_image,
)


class SourceImage(Timestampable):
    original = models.ImageField(upload_to=generic_upload_to)

    def create_mosaic_image(self, tile_size, **kwargs):
        mosaic_image = MosaicImage(
            source_image=self,
            tile_size=tile_size,
            **kwargs
        )
        if self.original.file.closed:
            self.original.open()
        with self.original.file as fp:
            o_im = Image.open(fp)
            normalized_image = normalize_source_image(o_im)
            mosaic_image.image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(normalized_image),
                save=True,
            )
        return mosaic_image


class MosaicImage(Timestampable):
    source_image = models.ForeignKey('SourceImage', related_name='mosaic_images')
    image = models.ImageField(upload_to=generic_upload_to)
    mosaic = models.ImageField(upload_to=generic_upload_to, null=True)

    TILE_SIZE_CHOICES = (
        (20, '20 pixels'),
    )
    tile_size = models.PositiveSmallIntegerField(choices=TILE_SIZE_CHOICES)

    def tiles_as_rows(self):
        key = operator.attrgetter('upper_left_y')
        for _, group_items in itertools.groupby(self.all_tiles.all(), key):
            yield tuple(group_items)

    def compose_mosaic(self):
        if self.all_tiles.filter(stock_tile_match__isnull=True).exists():
            raise ValueError("Cannot compose mosaic until all tiles are matched")
        size_x = self.image.width
        size_y = self.image.height
        mosaic_im = Image.new('RGB', (size_x, size_y))
        for tile in self.all_tiles.all():
            with tile.stock_tile_match.tile_image.file as fp:
                tile_im = Image.open(fp)
                mosaic_im.paste(
                    tile_im,
                    (
                        tile.upper_left_x,
                        tile.upper_left_y,
                        tile.upper_left_x + self.tile_size,
                        tile.upper_left_y + self.tile_size,
                    ),
                )
        self.mosaic.save(
            "{0}.png".format(str(uuid.uuid4())),
            convert_image_to_django_file(mosaic_im),
        )


class MosaicTile(models.Model):
    main_image = models.ForeignKey('MosaicImage', related_name='all_tiles')

    tile_image = models.ImageField(upload_to=generic_upload_to)
    tile_data = ArrayField(
        ArrayField(
            ArrayField(
                models.PositiveSmallIntegerField(),
            )
        )
    )

    stock_tile_match = models.ForeignKey(
        'NormalizedStockImage', null=True, on_delete=models.SET_NULL,
    )
    stock_tile_match_difference = models.PositiveIntegerField(null=True)

    upper_left_x = models.PositiveIntegerField()
    upper_left_y = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('main_image', 'upper_left_x', 'upper_left_y'),
        )
        ordering = ('upper_left_y', 'upper_left_x')

    @property
    def tile_size(self):
        return self.main_image.tile_size

    @property
    def lower_right_x(self):
        return self.upper_left_x + self.main_image.tile_size

    @property
    def lower_right_y(self):
        return self.upper_left_y + self.main_image.tile_size

    @property
    def scipy_tile_data(self):
        return cast_image_data_to_scipy_array(self.tile_data)


#
# Stock Images
#
class ImageSet(Timestampable):
    name = models.CharField(max_length=255)


class StockImage(Timestampable):
    original = models.ImageField(upload_to=generic_upload_to)

    image_hash = models.CharField(max_length=32, unique=True)
    is_invalid = models.BooleanField(default=False)

    @classmethod
    def create_from_filepath(cls, path):
        with open(path) as fp:
            image_hash = hashlib.md5(fp.read()).hexdigest()
            fp.seek(0)
            instance = cls(image_hash=image_hash)
            with Image.open(fp) as im:
                instance.original.save(
                    path,
                    convert_image_to_django_file(im),
                )
        return instance

    @classmethod
    def load_directory(cls, path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                image_path = os.path.join(dirpath, filename)
                with open(image_path) as im:
                    image_hash = hashlib.md5(im.read()).hexdigest()
                    if cls.objects.filter(image_hash=image_hash).exists():
                        continue

                    with transaction.atomic():
                        try:
                            with transaction.atomic():
                                stock_image = cls.create_from_filepath(image_path)
                        except IOError:
                            stock_image.is_invalid = True
                            stock_image.save()
                            continue

                        try:
                            NormalizedStockImage.create_from_stock_image(stock_image)
                        except ValueError:
                            stock_image.is_invalid = True
                            stock_image.save()


class NormalizedStockImage(Timestampable):
    stock_image = models.ForeignKey('StockImage', related_name='normalized_images')

    image = models.ImageField(upload_to=generic_upload_to)

    tile_image = models.ImageField(upload_to=generic_upload_to)
    tile_data = ArrayField(ArrayField(ArrayField(models.PositiveSmallIntegerField())))

    TILE_SIZE_CHOICES = MosaicImage.TILE_SIZE_CHOICES
    tile_size = models.PositiveSmallIntegerField(choices=TILE_SIZE_CHOICES)

    @classmethod
    def create_from_stock_image(cls, stock_image, tile_size=None):
        if tile_size is None:
            tile_size = cls.TILE_SIZE_CHOICES[0][0]
        instance = cls(stock_image=stock_image, tile_size=tile_size)
        if stock_image.original.file.closed:
            stock_image.original.file.open()
        else:
            stock_image.original.file.seek(0)
        with stock_image.original.file as fp:
            o_im = Image.open(fp).convert('RGB')
            im = normalize_stock_image(o_im, tile_size=tile_size)
            instance.image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(im),
                save=False,
            )
            tile_im = im.copy()
            tile_im.thumbnail((tile_size, tile_size))

            instance.tile_image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(tile_im),
            )
        return instance

    @property
    def scipy_tile_data(self):
        return cast_image_data_to_scipy_array(self.tile_data)


class StockImageTile(Timestampable):
    """
    TODO: figure out the right way to do this.
    """
    stock_image = models.ForeignKey('NormalizedStockImage', related_name='tiles')

    tile_image = models.ImageField(upload_to=generic_upload_to)
    tile_data = ArrayField(ArrayField(ArrayField(models.PositiveSmallIntegerField())))

    TILE_SIZE_CHOICES = (
        (20, '20 pixels'),
        (40, '40 pixels'),
    )
    tile_size = models.PositiveSmallIntegerField(choices=TILE_SIZE_CHOICES)

    @property
    def scipy_tile_data(self):
        return cast_image_data_to_scipy_array(self.tile_data)

    class Meta:
        abstract = True
