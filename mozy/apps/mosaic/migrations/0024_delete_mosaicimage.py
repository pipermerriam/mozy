# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0023_auto_20150414_1007'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MosaicImage',
        ),
    ]
