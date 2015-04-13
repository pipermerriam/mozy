# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0010_auto_20150412_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockimage',
            name='original',
            field=models.ImageField(null=True, upload_to=mozy.apps.core.utils.generic_upload_to),
            preserve_default=True,
        ),
    ]
