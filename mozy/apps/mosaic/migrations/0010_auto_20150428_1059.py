# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0009_auto_20150427_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tilegroup',
            name='group',
            field=models.ForeignKey(related_name='tile_matches', to='mosaic.Group'),
        ),
    ]
