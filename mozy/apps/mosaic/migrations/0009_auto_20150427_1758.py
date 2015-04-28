# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0008_group_stock_tiles'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tilegroup',
            unique_together=set([('group', 'stockimagetile')]),
        ),
    ]
