from __future__ import unicode_literals

import itertools
import os
import operator
import hashlib
import functools

from PIL import Image

from django.contrib.postgres.fields import ArrayField
from django.db import (
    models,
    transaction,
)
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from mozy.apps.core.utils import (
    uuid_filename,
    uuid_upload_to,
)
from mozy.apps.core.models import Timestampable

from mozy.apps.mosaic.utils import (
    cast_image_data_to_numpy_array,
    cast_numpy_array_to_python,
    convert_image_to_django_file,
    decompose_an_image,
    extract_pixel_data_from_image,
)
from mozy.apps.mosaic.normalization import (
    normalize_source_image,
    normalize_stock_image,
)
from mozy.apps.mosaic.managers import (
    SourceTileQuerySet,
)


class SourceImage(Timestampable):
    original = models.ImageField(upload_to=uuid_upload_to)

    def create_normalized_image(self, **kwargs):
        normalized_image = NormalizedSourceImage(
            source_image=self,
            **kwargs
        )
        if self.original.file.closed:
            self.original.open()
        with self.original.file as fp:
            o_im = Image.open(fp)
            im = normalize_source_image(o_im)
            normalized_image.image.save(
                uuid_filename(),
                convert_image_to_django_file(im),
                save=True,
            )
        return normalized_image


SOURCE_IMAGE_TILE_SIZE = 20


class NormalizedSourceImage(Timestampable):
    source_image = models.ForeignKey('SourceImage', related_name='normalized_images')
    image = models.ImageField(upload_to=uuid_upload_to)

    def tiles_as_rows(self):
        key = operator.attrgetter('y_coord')
        group_data = itertools.groupby(self.tiles.all(), key)
        return tuple((
            tuple(group_items) for _, group_items in group_data
        ))

    def get_stock_tile_hash(self):
        """
        Compute a hash that uniquely identifies a mosaic image based on the
        stock tiles that it is composed of.
        """
        if self.tiles.filter(stock_tile_match__isnull=True).exists():
            raise ValueError(
                "Cannot compute hash for NormalizedSourceImage: {0}.  Some "
                "tiles not matched".format(self.pk),
            )
        hash_str = ':'.join((
            str(v) for v in self.tiles.order_by('pk').values_list('stock_tile_match', flat=True)
        ))
        return hashlib.md5(hash_str).hexdigest()

    def create_tiles(self):
        if self.image.file.closed:
            self.image.file.open()

        tile_data = decompose_an_image(
            Image.open(self.image.file),
            tile_size=SOURCE_IMAGE_TILE_SIZE,
        )

        for box_coords, tile_image in tile_data.items():
            x_coord = box_coords[0] / SOURCE_IMAGE_TILE_SIZE
            y_coord = box_coords[1] / SOURCE_IMAGE_TILE_SIZE
            already_exists = self.tiles.filter(
                x_coord=x_coord,
                y_coord=y_coord,
            ).exists()

            if already_exists:
                continue

            tile_data = extract_pixel_data_from_image(tile_image)

            tile, _ = self.tiles.update_or_create(
                x_coord=x_coord,
                y_coord=y_coord,
                defaults={'tile_data': tile_data},
            )
            tile.tile_image.save(
                uuid_filename(),
                convert_image_to_django_file(tile_image),
                save=True
            )
            tile_image.close()

    def compose_mosaic(self, compose_tile_size=None, mosaic_image=None):
        """
        TODO: This method is toooo long and needs to be cleaned up.

        1. Gather appropriate parameters (compose_tile_size, ...)
        2. Validate that preconditions are met.
            - all tiles present
            - all tiles matched
            - all matched stock tiles have tile of correct size.
        3. Compose.
        """
        if compose_tile_size is None:
            if mosaic_image:
                compose_tile_size = mosaic_image.tile_size
            else:
                compose_tile_size = DEFAULT_MOSAIC_TILE_SIZE

        if self.tiles.filter(stock_tile_match__isnull=True).exists():
            raise ValueError("Cannot compose mosaic until all tiles are matched")

        num_available_tiles = self.tiles.filter(
            stock_tile_match__tiles__tile_size=compose_tile_size,
        ).distinct().count()

        if self.tiles.count() != num_available_tiles:
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
                mosaic_image = self.mosaic_images.exclude(
                    status=MosaicImage.STATUS_COMPLETE,
                ).get(
                    tile_size=compose_tile_size,
                    stock_tiles_hash=stock_tile_hash,
                )
                if not mosaic_image.is_pending and not mosaic_image.is_errored:
                    raise ValueError(
                        "Cannot compose mosaic for NormalizedSourceImage: {0}. "
                        "Image is neither pending nor is it errored".format(self.pk)
                    )
            except MosaicImage.DoesNotExist:
                mosaic_image = self.mosaic_images.create(
                    tile_size=compose_tile_size,
                    stock_tiles_hash=stock_tile_hash,
                    status=MosaicImage.STATUS_COMPOSING,
                )

        num_x_tiles = self.image.width / SOURCE_IMAGE_TILE_SIZE
        num_y_tiles = self.image.height / SOURCE_IMAGE_TILE_SIZE

        size_x = num_x_tiles * compose_tile_size
        size_y = num_y_tiles * compose_tile_size

        mosaic_im = Image.new('RGB', (size_x, size_y))

        for tile in self.tiles.all():
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
            uuid_filename(),
            convert_image_to_django_file(mosaic_im),
            save=True
        )
        return mosaic_image


@python_2_unicode_compatible
class SourceImageTile(Timestampable):
    MAX_TILE_PROCESSING_TIME = SourceTileQuerySet.MAX_TILE_PROCESSING_TIME

    main_image = models.ForeignKey('NormalizedSourceImage', related_name='tiles')

    tile_image = models.ImageField(upload_to=uuid_upload_to)
    tile_data = ArrayField(
        ArrayField(
            ArrayField(
                models.PositiveSmallIntegerField(),
            )
        )
    )

    task_lock = models.UUIDField(null=True)

    stock_tile_match = models.ForeignKey(
        'NormalizedStockImage', null=True, on_delete=models.SET_NULL,
    )
    stock_tile_match_difference = models.PositiveIntegerField(null=True)

    x_coord = models.PositiveSmallIntegerField(null=True)
    y_coord = models.PositiveSmallIntegerField(null=True)

    objects = SourceTileQuerySet.as_manager()

    class Meta:
        unique_together = (
            ('main_image', 'x_coord', 'y_coord'),
        )
        ordering = ('y_coord', 'x_coord')

    def __str__(self):
        return "x:{0} y:{1}".format(self.x_coord, self.y_coord)

    @classmethod
    def get_errored_datetime(cls):
        return timezone.now() - timezone.timedelta(hours=2)

    @property
    def numpy_tile_data(self):
        return cast_image_data_to_numpy_array(self.tile_data)

    @property
    def upper_left_x(self):
        return self.x_coord * SOURCE_IMAGE_TILE_SIZE

    @property
    def upper_left_y(self):
        return self.y_coord * SOURCE_IMAGE_TILE_SIZE

    @property
    def lower_right_x(self):
        return self.upper_left_x + SOURCE_IMAGE_TILE_SIZE

    @property
    def lower_right_y(self):
        return self.upper_left_y + SOURCE_IMAGE_TILE_SIZE

    def get_image_box(self, tile_size):
        return (
            self.x_coord * tile_size,
            self.y_coord * tile_size,
            self.x_coord * tile_size + tile_size,
            self.y_coord * tile_size + tile_size,
        )


DEFAULT_MOSAIC_TILE_SIZE = 40
TILE_SIZE_CHOICES = (
    (20, '20 pixels'),
    (40, '40 pixels'),
    (60, '60 pixels'),
    (80, '80 pixels'),
)


class MosaicImage(Timestampable):
    image = models.ForeignKey('NormalizedSourceImage', related_name='mosaic_images')

    mosaic = models.ImageField(upload_to=uuid_upload_to, null=True)

    TILE_SIZE_CHOICES = TILE_SIZE_CHOICES
    tile_size = models.PositiveSmallIntegerField(
        choices=TILE_SIZE_CHOICES, default=DEFAULT_MOSAIC_TILE_SIZE,
    )

    stock_tiles_hash = models.CharField(max_length=255, db_index=True)

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
                    uuid_filename(extension),
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
                uuid_filename(),
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


class Lineage(Timestampable):
    k = models.PositiveIntegerField()

    def create_next_generation(self):
        last_generation = self.generations.last()
        if last_generation:
            next_index = last_generation.index + 1
        else:
            next_index = 0
        return self.generations.create(index=next_index)

    def generate(self, until_generation=None):
        if not self.generations.exists():
            generation = self.create_next_generation()
            print "Created Generation #{0}".format(generation.index)
        else:
            generation = self.generations.last()
            print "Resuming Generation #{0}".format(generation.index)

        while True:
            if generation.groups.count() < self.k:
                generation.create_groups()
                print "Created Generation #{0} groups".format(generation.index)
            assert generation.groups.count() == self.k
            generation.classify_stock_data()
            print "Finished classifying stock data for generation #{0}".format(generation.index)
            if until_generation and generation.index >= until_generation:
                break
            generation = self.create_next_generation()
            print "Created Generation #", generation.index


class Generation(Timestampable):
    lineage = models.ForeignKey('Lineage', related_name='generations')
    index = models.PositiveIntegerField()

    def create_groups(self):
        previous_generation = self.lineage.generations.filter(
            index__lt=self.index,
        ).order_by('-index').first()
        if previous_generation:
            total_stock_tiles = StockImageTile.objects.filter(tile_size=20).count()
            accounted_for_tiles = StockImageTile.objects.filter(
                groups__generation=previous_generation,
                tile_size=20,
            ).count()
            if accounted_for_tiles != total_stock_tiles:
                raise ValueError("Not all tiles matched")
            num_to_create = self.lineage.k - self.groups.count()
            groups_needing_children = previous_generation.groups.filter(
                child__isnull=True,
            )[:num_to_create]
            for group in groups_needing_children:
                if group.stock_tiles.count() > 15:
                    center = group.get_actual_center()
                    parent = group
                else:
                    continue
                self.groups.create(
                    parent=parent,
                    center=center,
                )
            num_missing = self.lineage.k - self.groups.count()
            for _ in range(num_missing):
                center = StockImageTile.objects.filter(
                    tile_size=20,
                ).order_by('?')[0].tile_data
                self.groups.create(
                    center=center,
                    parent=None,
                )
        else:
            centers = StockImageTile.objects.filter(
                tile_size=20,
            ).order_by('?').values_list(
                'tile_data', flat=True,
            )[:self.lineage.k]
            for center in centers:
                self.groups.create(
                    center=center,
                )

    def classify_stock_data(self):
        """
        Loop over the stock tile database and group the images based on this
        generation's center points.
        """
        from mozy.apps.mosaic.stock_data import (
            InMemoryGroupDataBackend,
        )
        from mozy.apps.mosaic.exclusions import DummyExclusions
        from mozy.apps.mosaic.backends.brute import find_tile_matches

        group_data = InMemoryGroupDataBackend(generation=self)
        exclusions = DummyExclusions()

        matcher = functools.partial(
            find_tile_matches,
            stock_data=group_data,
            exclusions=exclusions,
            match_threshold=0,
        )

        tile_qs = tuple(StockImageTile.objects.exclude(
            groups__generation=self,
        ).filter(
            tile_size=20,
        ).values_list('pk', 'tile_data'))

        instances = []
        for tile_pk, tile_data in tile_qs:
            match_data = matcher((
                (tile_pk, cast_image_data_to_numpy_array(tile_data)),
            ))
            stock_tile_pk, group_pk, difference = match_data[0]
            instances.append(TileGroup(
                stockimagetile_id=stock_tile_pk,
                group_id=group_pk,
                difference=difference,
            ))
            if len(instances) > 500:
                TileGroup.objects.bulk_create(instances)
                instances = []
        if len(instances):
            TileGroup.objects.bulk_create(instances)

    class Meta:
        unique_together = (
            ('lineage', 'index')
        )
        ordering = ('index',)


class TileGroup(models.Model):
    group = models.ForeignKey('Group', related_name='tile_matches')
    stockimagetile = models.ForeignKey('StockImageTile')
    difference = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('group', 'stockimagetile'),
        )


class Group(Timestampable):
    generation = models.ForeignKey('Generation', related_name='groups')
    parent = models.OneToOneField('self', related_name='child', null=True)
    stock_tiles = models.ManyToManyField(
        'StockImageTile', related_name='groups', through='TileGroup',
    )

    center = ArrayField(
        ArrayField(ArrayField(models.PositiveSmallIntegerField())),
    )

    @property
    def numpy_center(self):
        return cast_image_data_to_numpy_array(self.center)

    def get_actual_center(self):
        import numpy
        return cast_numpy_array_to_python(numpy.mean(tuple((
            cast_image_data_to_numpy_array(tile_data)
            for tile_data in self.stock_tiles.values_list('tile_data', flat=True)
        )), axis=0))

    @property
    def differences(self):
        import numpy
        return numpy.array(tuple(self.tile_matches.values_list('difference', flat=True)))
