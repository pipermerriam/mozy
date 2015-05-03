# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0009_auto_20150502_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='normalizedsourceimage',
            name='task_lock',
            field=models.UUIDField(null=True),
        ),
    ]
