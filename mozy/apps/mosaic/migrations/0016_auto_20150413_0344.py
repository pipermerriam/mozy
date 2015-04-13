# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0015_mosaictile_stock_tile_match_difference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mosaictile',
            name='tile_data',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None),
        ),
    ]
