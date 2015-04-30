# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mosaicimage',
            name='status',
            field=models.CharField(default=b'pending', max_length=50, db_index=True, choices=[(b'pending', b'Pending'), (b'composing', b'Composing'), (b'complete', b'Complete')]),
        ),
        migrations.AlterField(
            model_name='mosaicimage',
            name='stock_tiles_hash',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='normalizedsourceimage',
            name='tile_size',
            field=models.PositiveSmallIntegerField(default=20, choices=[(20, b'20 pixels')]),
        ),
        migrations.AlterField(
            model_name='sourceimagetile',
            name='status',
            field=models.CharField(default=b'pending', max_length=50, db_index=True, choices=[(b'pending', b'Pending'), (b'queud', b'Queued'), (b'matching', b'Matching'), (b'matched', b'Matched')]),
        ),
    ]
