# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0025_auto_20150414_1022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mosaicimage',
            name='image',
            field=models.ForeignKey(related_name='mosaic_images', to='mosaic.NormalizedSourceImage'),
        ),
    ]
