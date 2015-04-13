# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0003_auto_20150411_2114'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NormalizedStockImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to=mozy.apps.core.utils.generic_upload_to)),
                ('tile_size', models.PositiveSmallIntegerField(choices=[(20, b'20 pixels')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('original', models.ImageField(upload_to=mozy.apps.core.utils.generic_upload_to)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='normalizedstockimage',
            name='stock_image',
            field=models.ForeignKey(to='mosaic.StockImage'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='normalizedstockimage',
            unique_together=set([('stock_image', 'tile_size')]),
        ),
        migrations.AlterModelOptions(
            name='mosaictile',
            options={'ordering': ('upper_left_y', 'upper_left_x')},
        ),
        migrations.AddField(
            model_name='mosaictile',
            name='stock_tile_match',
            field=models.ForeignKey(to='mosaic.NormalizedStockImage', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mosaictile',
            name='main_image',
            field=models.ForeignKey(related_name='all_tiles', to='mosaic.MosaicImage'),
            preserve_default=True,
        ),
    ]
