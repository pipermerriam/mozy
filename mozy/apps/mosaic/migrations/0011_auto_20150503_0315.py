# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0010_normalizedsourceimage_task_lock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mosaicimage',
            name='mosaic',
            field=models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to),
        ),
    ]
