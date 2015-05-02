# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0004_auto_20150502_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='normalizedsourceimage',
            name='tile_size',
        ),
        migrations.AlterField(
            model_name='mosaicimage',
            name='tile_size',
            field=models.PositiveSmallIntegerField(default=40, choices=[(20, b'20 pixels'), (40, b'40 pixels'), (60, b'60 pixels'), (80, b'80 pixels')]),
        ),
    ]
