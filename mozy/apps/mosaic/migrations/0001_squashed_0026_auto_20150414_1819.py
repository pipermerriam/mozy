# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
import django.contrib.postgres.fields
import mozy.apps.core.utils


class Migration(migrations.Migration):

    replaces = [(b'mosaic', '0001_initial'), (b'mosaic', '0002_auto_20150411_2055'), (b'mosaic', '0003_auto_20150411_2114'), (b'mosaic', '0004_auto_20150412_0704'), (b'mosaic', '0005_normalizedstockimage_tile_image'), (b'mosaic', '0006_auto_20150412_1020'), (b'mosaic', '0007_auto_20150412_1837'), (b'mosaic', '0008_auto_20150412_1838'), (b'mosaic', '0009_stockimage_is_invalid'), (b'mosaic', '0010_auto_20150412_1857'), (b'mosaic', '0011_auto_20150412_1913'), (b'mosaic', '0012_auto_20150412_1918'), (b'mosaic', '0013_mosaicimage_mosaic'), (b'mosaic', '0014_auto_20150413_0202'), (b'mosaic', '0015_mosaictile_stock_tile_match_difference'), (b'mosaic', '0016_auto_20150413_0344'), (b'mosaic', '0017_auto_20150413_0344'), (b'mosaic', '0018_auto_20150413_0411'), (b'mosaic', '0019_auto_20150413_0957'), (b'mosaic', '0020_stockimagetile'), (b'mosaic', '0021_auto_20150414_0936'), (b'mosaic', '0022_auto_20150414_0941'), (b'mosaic', '0023_auto_20150414_1007'), (b'mosaic', '0024_delete_mosaicimage'), (b'mosaic', '0025_auto_20150414_1022'), (b'mosaic', '0026_auto_20150414_1819')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MosaicImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MosaicTile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('main_image', models.ForeignKey(to='mosaic.MosaicImage')),
                ('tile_image', models.ImageField(default=None, upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('upper_left_x', models.PositiveIntegerField(default=1)),
                ('upper_left_y', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='SourceImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('original', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='source_image',
            field=models.ForeignKey(related_name='mosaic_images', to='mosaic.SourceImage'),
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='tile_size',
            field=models.PositiveSmallIntegerField(default=20, choices=[(20, b'20 pixels')]),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='mosaictile',
            unique_together=set([('main_image', 'upper_left_x', 'upper_left_y')]),
        ),
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
        ),
        migrations.CreateModel(
            name='NormalizedStockImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('tile_size', models.PositiveSmallIntegerField(choices=[(20, b'20 pixels')])),
            ],
        ),
        migrations.CreateModel(
            name='StockImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('original', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('image_hash', models.CharField(unique=True, max_length=32)),
                ('is_invalid', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='normalizedstockimage',
            name='stock_image',
            field=models.ForeignKey(to='mosaic.StockImage'),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mosaic.NormalizedStockImage', null=True),
        ),
        migrations.AlterField(
            model_name='mosaictile',
            name='main_image',
            field=models.ForeignKey(related_name='all_tiles', to='mosaic.MosaicImage'),
        ),
        migrations.AddField(
            model_name='normalizedstockimage',
            name='tile_image',
            field=models.ImageField(default='', upload_to=mozy.apps.core.utils.uuid_upload_to),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='normalizedstockimage',
            name='stock_image',
            field=models.ForeignKey(related_name='normalized_images', to='mosaic.StockImage'),
        ),
        migrations.AlterUniqueTogether(
            name='normalizedstockimage',
            unique_together=set([]),
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='mosaic',
            field=models.ImageField(null=True, upload_to=mozy.apps.core.utils.uuid_upload_to),
        ),
        migrations.AddField(
            model_name='mosaictile',
            name='tile_data',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None),
        ),
        migrations.AddField(
            model_name='normalizedstockimage',
            name='tile_data',
            field=django.contrib.postgres.fields.ArrayField(default=None, base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mosaictile',
            name='stock_tile_match_difference',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.CreateModel(
            name='StockImageTile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tile_image', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('tile_data', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None)),
                ('tile_size', models.PositiveSmallIntegerField(choices=[(20, b'20 pixels'), (40, b'40 pixels')])),
                ('stock_image', models.ForeignKey(related_name='tiles', to='mosaic.NormalizedStockImage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameModel(
            old_name='MosaicTile',
            new_name='SourceImageTile',
        ),
        migrations.RenameModel(
            old_name='MosaicImage',
            new_name='NormalizedSourceImage',
        ),
        migrations.RemoveField(
            model_name='normalizedsourceimage',
            name='mosaic',
        ),
        migrations.RemoveField(
            model_name='normalizedstockimage',
            name='tile_data',
        ),
        migrations.RemoveField(
            model_name='normalizedstockimage',
            name='tile_image',
        ),
        migrations.RemoveField(
            model_name='normalizedstockimage',
            name='tile_size',
        ),
        migrations.CreateModel(
            name='MosaicImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mosaic', models.ImageField(null=True, upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('tile_size', models.PositiveSmallIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='normalizedsourceimage',
            name='source_image',
            field=models.ForeignKey(related_name='normalized_images', to='mosaic.SourceImage'),
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='image',
            field=models.ForeignKey(related_name='mosaic_images', to='mosaic.NormalizedSourceImage'),
        ),
    ]
