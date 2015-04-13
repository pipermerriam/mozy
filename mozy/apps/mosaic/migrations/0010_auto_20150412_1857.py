# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0009_stockimage_is_invalid'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='normalizedstockimage',
            unique_together=set([]),
        ),
    ]
