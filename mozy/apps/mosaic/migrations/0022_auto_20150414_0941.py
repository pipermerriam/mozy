# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0021_auto_20150414_0936'),
    ]

    operations = [
        migrations.RenameModel('MosaicImage', 'NormalizedSourceImage'),
    ]
