# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0006_auto_20150412_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockimage',
            name='image_hash',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mosaictile',
            name='stock_tile_match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mosaic.NormalizedStockImage', null=True),
            preserve_default=True,
        ),
    ]
