# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0007_auto_20150412_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockimage',
            name='image_hash',
            field=models.CharField(unique=True, max_length=32),
            preserve_default=True,
        ),
    ]
