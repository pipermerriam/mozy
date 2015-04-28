# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0007_auto_20150427_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='stock_tiles',
            field=models.ManyToManyField(related_name='groups', through='mosaic.TileGroup', to='mosaic.StockImageTile'),
        ),
    ]
