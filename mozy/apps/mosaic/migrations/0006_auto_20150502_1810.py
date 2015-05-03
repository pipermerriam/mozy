# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0005_auto_20150502_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourceimagetile',
            name='x_coord',
            field=models.PositiveSmallIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='sourceimagetile',
            name='y_coord',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
