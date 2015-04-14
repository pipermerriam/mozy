# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.contrib.postgres.fields
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0019_auto_20150413_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockImageTile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tile_image', models.ImageField(upload_to=mozy.apps.core.utils.generic_upload_to)),
                ('tile_data', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None)),
                ('tile_size', models.PositiveSmallIntegerField(choices=[(20, b'20 pixels'), (40, b'40 pixels')])),
                ('stock_image', models.ForeignKey(related_name='tiles', to='mosaic.NormalizedStockImage')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
