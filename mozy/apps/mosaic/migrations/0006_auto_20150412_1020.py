# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0005_normalizedstockimage_tile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='normalizedstockimage',
            name='stock_image',
            field=models.ForeignKey(related_name='normalized_images', to='mosaic.StockImage'),
            preserve_default=True,
        ),
    ]
