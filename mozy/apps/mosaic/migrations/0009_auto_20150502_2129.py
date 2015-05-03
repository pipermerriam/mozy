# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0008_auto_20150502_1841'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mosaicimage',
            name='status',
        ),
        migrations.RemoveField(
            model_name='sourceimagetile',
            name='status',
        ),
        migrations.AddField(
            model_name='sourceimagetile',
            name='task_lock',
            field=models.UUIDField(null=True),
        ),
    ]
