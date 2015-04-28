# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0005_auto_20150427_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='parent',
            field=models.OneToOneField(related_name='child', null=True, to='mosaic.Group'),
        ),
    ]
