# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0003_auto_20150430_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sourceimagetile',
            name='main_image',
            field=models.ForeignKey(related_name='tiles', to='mosaic.NormalizedSourceImage'),
        ),
    ]
