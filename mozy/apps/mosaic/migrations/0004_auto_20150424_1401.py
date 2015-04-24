# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0003_sourceimagetile_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourceimagetile',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='sourceimagetile',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 24, 21, 1, 24, 177419, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
