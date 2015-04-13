# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0004_auto_20150412_0704'),
    ]

    operations = [
        migrations.AddField(
            model_name='normalizedstockimage',
            name='tile_image',
            field=models.ImageField(default='', upload_to=mozy.apps.core.utils.generic_upload_to),
            preserve_default=False,
        ),
    ]
