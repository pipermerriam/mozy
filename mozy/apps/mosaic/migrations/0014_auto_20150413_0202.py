# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0013_mosaicimage_mosaic'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaictile',
            name='tile_data',
            field=django.contrib.postgres.fields.ArrayField(default=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='normalizedstockimage',
            name='tile_data',
            field=django.contrib.postgres.fields.ArrayField(default=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None),
            preserve_default=False,
        ),
    ]
