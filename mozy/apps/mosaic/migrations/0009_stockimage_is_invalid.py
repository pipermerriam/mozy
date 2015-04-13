# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0008_auto_20150412_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockimage',
            name='is_invalid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
