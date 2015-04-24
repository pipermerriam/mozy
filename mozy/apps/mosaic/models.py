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
from django.utils import timezone

from mozy.apps.core.utils import uuid_upload_to
from mozy.apps.core.models import Timestampable

from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
    convert_image_to_django_file,
    normalize_source_image,
    normalize_stock_image,
)


class SourceImage(Timestampable):
    original = models.ImageField(upload_to=uuid_upload_to)

    def create_normalize_image(self, tile_size, **kwargs):
        normalized_image = NormalizedSourceImage(
            source_image=self,
            tile_size=tile_size,
            **kwargs
        )
        if self.original.file.closed:
            self.original.open()
        with self.original.file as fp:
            o_im = Image.open(fp)
            im = normalize_source_image(o_im)
            normalized_image.image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(im),
                save=True,
            )
        return normalized_image


class NormalizedSourceImage(Timestampable):
    source_image = models.ForeignKey('SourceImage', related_name='normalized_images')
    image = models.ImageField(upload_to=uuid_upload_to)

    TILE_SIZE_CHOICES = (
        (20, '20 pixels'),
    )
    tile_size = models.PositiveSmallIntegerField(choices=TILE_SIZE_CHOICES)

    def tiles_as_rows(self):
        key = operator.attrgetter('upper_left_y')
        for _, group_items in itertools.groupby(self.all_tiles.all(), key):
            yield tuple(group_items)

    def get_stock_tile_hash(self):
        """
        Compute a hash that uniquely identifies a mosaic image based on the
        stock tiles that it is composed of.
        """
        if self.all_tiles.filter(stock_tile_match__isnull=True).exists():
            raise ValueError(
                "Cannot compute hash for NormalizedSourceImage: {0}.  Some "
                "tiles not matched".format(self.pk),
            )
        hash_str = ':'.join((
            str(v) for v in self.all_tiles.order_by('pk').values_list('stock_tile_match', flat=True)
        ))
        return hashlib.md5(hash_str).hexdigest()

    def compose_mosaic(self, compose_tile_size=None, mosaic_image=None):
        if compose_tile_size is None:
            if mosaic_image:
                compose_tile_size = mosaic_image.tile_size
            else:
                compose_tile_size = self.tile_size

        if self.all_tiles.filter(stock_tile_match__isnull=True).exists():
            raise ValueError("Cannot compose mosaic until all tiles are matched")

        num_available_tiles = self.all_tiles.filter(
            stock_tile_match__tiles__tile_size=compose_tile_size,
        ).distinct().count()

        if self.all_tiles.count() != num_available_tiles:
            raise ValueError(
                "Cannot compose mosaic.  Not all matched stock images have a "
                "tile of the right size"
            )

        stock_tile_hash = self.get_stock_tile_hash()
        if mosaic_image:
            if mosaic_image.tile_size != compose_tile_size:
                raise ValueError(
                    "Tile size: {0} != Compose size: {1} for "
                    "NormalizedSourceImage: {2} and MosaicImage: {3}".format(
                        mosaic_image.tile_size, compose_tile_size,
                        self.pk, mosaic_image.pk,
                    )
                )
        else:
            try:
                mosaic_image = self.mosaic_images.get(
                    tile_size=compose_tile_size,
                    stock_tile_hash=stock_tile_hash,
                )
                if not mosaic_image.is_pending and not mosaic_image.is_errored:
                    raise ValueError(
                        "Cannot compose mosaic for NormalizedSourceImage: {0}. "
                        "Image is neither pending nor is it errored".format(self.pk)
                    )
            except MosaicImage.DoesNotExist:
                mosaic_image = self.mosaic_images.create(
                    tile_size=compose_tile_size,
                    stock_tile_hash=stock_tile_hash,
                    status=MosaicImage.STATUS_COMPOSING,
                )

        num_x_tiles = self.image.width / self.tile_size
        num_y_tiles = self.image.height / self.tile_size

        size_x = num_x_tiles * compose_tile_size
        size_y = num_y_tiles * compose_tile_size

        mosaic_im = Image.new('RGB', (size_x, size_y))

        for tile in self.all_tiles.all():
            stock_tile = tile.stock_tile_match.tiles.get(
                tile_size=compose_tile_size,
            )
            with stock_tile.tile_image.file as fp:
                tile_im = Image.open(fp)
                mosaic_im.paste(
                    tile_im,
                    tile.get_image_box(compose_tile_size),
                )
        mosaic_image.mosaic.save(
            "{0}.png".format(str(uuid.uuid4())),
            convert_image_to_django_file(mosaic_im),
            save=True
        )
        return mosaic_image


class SourceImageTile(models.Model):
    main_image = models.ForeignKey('NormalizedSourceImage', related_name='all_tiles')

    tile_image = models.ImageField(upload_to=uuid_upload_to)
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
    def numpy_tile_data(self):
        return cast_image_data_to_numpy_array(self.tile_data)

    def get_image_box(self, tile_size=None):
        if tile_size is None:
            tile_size = self.tile_size
        return (
            (self.upper_left_x / self.tile_size) * tile_size,
            (self.upper_left_y / self.tile_size) * tile_size,
            (self.upper_left_x / self.tile_size) * tile_size + tile_size,
            (self.upper_left_y / self.tile_size) * tile_size + tile_size,
        )


class MosaicImage(Timestampable):
    image = models.ForeignKey('NormalizedSourceImage', related_name='mosaic_images')

    mosaic = models.ImageField(upload_to=uuid_upload_to, null=True)
    tile_size = models.PositiveSmallIntegerField()

    STATUS_PENDING = 'pending'
    STATUS_COMPOSING = 'composing'
    STATUS_COMPLETE = 'complete'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPOSING, 'Composing'),
        (STATUS_COMPLETE, 'Complete'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    stock_tiles_hash = models.CharField(max_length=255)

    class Meta:
        unique_together = (
            ('image', 'tile_size', 'stock_tiles_hash'),
        )

    @classmethod
    def get_errored_datetime(cls):
        return timezone.now() - timezone.timedelta(hours=1)

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_composing(self):
        return self.status == self.STATUS_COMPOSING

    @property
    def is_complete(self):
        return self.status == self.STATUS_COMPLETE

    @property
    def is_errored(self):
        if self.is_composing and self.updated_at <= self.get_errored_datetime():
            return True
        return False


#
# Stock Images
#
class ImageSet(Timestampable):
    name = models.CharField(max_length=255)


class StockImage(Timestampable):
    original = models.ImageField(upload_to=uuid_upload_to)

    image_hash = models.CharField(max_length=32, unique=True)
    is_invalid = models.BooleanField(default=False)

    @classmethod
    def create_from_filepath(cls, path):
        with open(path) as fp:
            image_hash = hashlib.md5(fp.read()).hexdigest()
            fp.seek(0)
            instance = cls(image_hash=image_hash)
            extension = path.rpartition('.')[2]
            with Image.open(fp) as im:
                instance.original.save(
                    "{0}.{1}".format(uuid.uuid4(), extension),
                    convert_image_to_django_file(im),
                )
        return instance

    @classmethod
    def load_directory(cls, path):
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                image_path = os.path.join(dirpath, filename)
                with open(image_path) as im:
                    image_hash = hashlib.md5(im.read()).hexdigest()
                    if cls.objects.filter(image_hash=image_hash).exists():
                        print "already exists"
                        continue

                    with transaction.atomic():
                        try:
                            with transaction.atomic():
                                stock_image = cls.create_from_filepath(image_path)
                        except IOError as exc:
                            print "IOError", exc
                            cls.objects.create(
                                original=None,
                                image_hash=image_hash,
                                is_invalid=True,
                            )
                            continue

                        try:
                            NormalizedStockImage.create_from_stock_image(stock_image)
                        except ValueError as exc:
                            print "ValueError", exc
                            stock_image.is_invalid = True
                            stock_image.save()


class NormalizedStockImage(Timestampable):
    stock_image = models.ForeignKey('StockImage', related_name='normalized_images')

    image = models.ImageField(upload_to=uuid_upload_to)

    @classmethod
    def create_from_stock_image(cls, stock_image):
        instance = cls(stock_image=stock_image)
        if stock_image.original.file.closed:
            stock_image.original.file.open()
        else:
            stock_image.original.file.seek(0)
        with stock_image.original.file as fp:
            o_im = Image.open(fp).convert('RGB')
            # TODO: A fixed tile size of 20 imposes some subtle constraints on
            # generating mosaics using non-20-sized tiles.
            im = normalize_stock_image(o_im, tile_size=20)
            instance.image.save(
                "{0}.png".format(str(uuid.uuid4())),
                convert_image_to_django_file(im),
                save=True,
            )
        return instance

    @property
    def numpy_tile_data(self):
        return cast_image_data_to_numpy_array(self.tile_data)


class StockImageTile(Timestampable):
    """
    TODO: figure out the right way to do this.
    """
    stock_image = models.ForeignKey('NormalizedStockImage', related_name='tiles')

    tile_image = models.ImageField(upload_to=uuid_upload_to)
    tile_data = ArrayField(ArrayField(ArrayField(models.PositiveSmallIntegerField())))

    TILE_SIZE_CHOICES = (
        (20, '20 pixels'),
        (40, '40 pixels'),
    )
    tile_size = models.PositiveSmallIntegerField(choices=TILE_SIZE_CHOICES)

    @property
    def numpy_tile_data(self):
        return cast_image_data_to_numpy_array(self.tile_data)
