# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0006_auto_20150427_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='TileGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('difference', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='group',
            name='stock_tiles',
        ),
        migrations.AddField(
            model_name='tilegroup',
            name='group',
            field=models.ForeignKey(to='mosaic.Group'),
        ),
        migrations.AddField(
            model_name='tilegroup',
            name='stockimagetile',
            field=models.ForeignKey(to='mosaic.StockImageTile'),
        ),
    ]
