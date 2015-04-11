from django.db import models

from mozy.apps.core.utils import generic_upload_to
from mozy.apps.core.models import Timestampable


class SourceImage(Timestampable):
    original = models.ImageField(upload_to=generic_upload_to)


class MosaicImage(Timestampable):
    image = models.ImageField(upload_to=generic_upload_to)


class MosaicTile(models.Model):
    main_image = models.ForeignKey('MosaicImage')
    tile_image = models.ImageField(upload_to=generic_upload_to)

    upper_left_x = models.PositiveIntegerField()
    upper_left_y = models.PositiveIntegerField()

    tile_size = models.PositiveSmallIntegerField()

    @property
    def lower_right_x(self):
        return self.upper_left_x + self.tile_size

    @property
    def lower_right_y(self):
        return self.upper_left_y + self.tile_size
