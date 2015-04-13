# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0012_auto_20150412_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='mosaicimage',
            name='mosaic',
            field=models.ImageField(null=True, upload_to=mozy.apps.core.utils.generic_upload_to),
            preserve_default=True,
        ),
    ]
