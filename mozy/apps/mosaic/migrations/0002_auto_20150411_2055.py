# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaicimage',
            name='source_image',
            field=models.ForeignKey(default='', to='mosaic.SourceImage'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='tile_size',
            field=models.PositiveSmallIntegerField(default=20, choices=[(20, b'20 pixels')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mosaictile',
            name='tile_image',
            field=models.ImageField(default=None, upload_to=mozy.apps.core.utils.generic_upload_to),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mosaictile',
            name='upper_left_x',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mosaictile',
            name='upper_left_y',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
