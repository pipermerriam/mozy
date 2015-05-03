# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0007_auto_20150502_1810'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sourceimagetile',
            options={'ordering': ('y_coord', 'x_coord')},
        ),
        migrations.AlterUniqueTogether(
            name='sourceimagetile',
            unique_together=set([('main_image', 'x_coord', 'y_coord')]),
        ),
        migrations.RemoveField(
            model_name='sourceimagetile',
            name='upper_left_x',
        ),
        migrations.RemoveField(
            model_name='sourceimagetile',
            name='upper_left_y',
        ),
    ]
