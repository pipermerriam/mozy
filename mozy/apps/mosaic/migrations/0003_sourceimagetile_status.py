# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0002_auto_20150424_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourceimagetile',
            name='status',
            field=models.CharField(default='pending', max_length=50, choices=[(b'pending', b'Pending'), (b'queud', b'Queued'), (b'matching', b'Matching'), (b'matched', b'Matched')]),
            preserve_default=False,
        ),
    ]
