# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0020_stockimagetile'),
    ]

    operations = [
        migrations.RenameModel('MosaicTile', 'SourceImageTile'),
    ]
