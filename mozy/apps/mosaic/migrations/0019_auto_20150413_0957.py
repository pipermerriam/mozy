# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0018_auto_20150413_0411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mosaicimage',
            name='source_image',
            field=models.ForeignKey(related_name='mosaic_images', to='mosaic.SourceImage'),
        ),
    ]
