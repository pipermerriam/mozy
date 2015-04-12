import itertools
import uuid

import StringIO

from django.core.files import File
from django.db import models

from mozy.apps.core.utils import generic_upload_to
from mozy.apps.core.models import Timestampable


class SourceImage(Timestampable):
    original = models.ImageField(upload_to=generic_upload_to)


class MosaicImage(Timestampable):
    source_image = models.ForeignKey('SourceImage')
    image = models.ImageField(upload_to=generic_upload_to)

    TILE_SIZE_CHOICES = (
        (20, '20 pixels'),
    )
    tile_size = models.PositiveSmallIntegerField(choices=TILE_SIZE_CHOICES)

    def populate_image(self, image):
        image_file = StringIO.StringIO()
        image.save(image_file, format='PNG')
        self.image.save(
            generic_upload_to(self, '{0}.png'.format(str(uuid.uuid4()))),
            File(image_file),
            save=False,
        )

    def tiles_as_rows(self):
        for group, group_items in itertools.groupby(self.all_tiles.all(), lambda t: t.upper_left_y):
            yield tuple(group_items)


class MosaicTile(models.Model):
    main_image = models.ForeignKey('MosaicImage', related_name='all_tiles')
    tile_image = models.ImageField(upload_to=generic_upload_to)

    upper_left_x = models.PositiveIntegerField()
    upper_left_y = models.PositiveIntegerField()

    class Meta:
        unique_together = (
            ('main_image', 'upper_left_x', 'upper_left_y'),
        )
        ordering = ('upper_left_y', 'upper_left_x')

    @property
    def lower_right_x(self):
        return self.upper_left_x + self.main_image.tile_size

    @property
    def lower_right_y(self):
        return self.upper_left_y + self.main_image.tile_size

    def populate_tile(self, image):
        image_file = StringIO.StringIO()
        image.save(image_file, format='PNG')
        self.tile_image.save(
            generic_upload_to(self, '{0}.png'.format(str(uuid.uuid4()))),
            File(image_file),
            save=False,
        )
