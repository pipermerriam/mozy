# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0002_auto_20150411_2055'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mosaictile',
            unique_together=set([('main_image', 'upper_left_x', 'upper_left_y')]),
        ),
    ]
