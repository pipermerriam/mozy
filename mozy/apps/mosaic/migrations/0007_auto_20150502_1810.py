# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def populate_coords(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    SourceImageTile = apps.get_model('mosaic', 'SourceImageTile')
    if not SourceImageTile.objects.exists():
        # empty database
        return

    F = models.F

    SourceImageTile.objects.update(x_coord=F('upper_left_x') / 20)
    SourceImageTile.objects.update(y_coord=F('upper_left_y') / 20)

    if SourceImageTile.objects.filter(x_coord__isnull=True).exists():
        raise ValueError('something is wrong')
    if SourceImageTile.objects.filter(y_coord__isnull=True).exists():
        raise ValueError('something is wrong')

    # random sample of 20 records to be sure it worked.
    for _ in range(20):
        tile = SourceImageTile.objects.order_by('?').first()
        if tile.x_coord != tile.upper_left_x / 20:
            raise ValueError('something is wrong')
        if tile.y_coord != tile.upper_left_y / 20:
            raise ValueError('something is wrong')


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0006_auto_20150502_1810'),
    ]

    operations = [
        migrations.RunPython(populate_coords),
    ]
