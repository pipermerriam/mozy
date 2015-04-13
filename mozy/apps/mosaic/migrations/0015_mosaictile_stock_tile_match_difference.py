# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0014_auto_20150413_0202'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaictile',
            name='stock_tile_match_difference',
            field=models.PositiveIntegerField(default=1000000000.0),
            preserve_default=False,
        ),
    ]
