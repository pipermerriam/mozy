# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0016_auto_20150413_0344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mosaictile',
            name='stock_tile_match_difference',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
