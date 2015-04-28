# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Generation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('index', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('index',),
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('center', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None)),
                ('generation', models.ForeignKey(related_name='groups', to='mosaic.Generation')),
                ('parent', models.OneToOneField(related_name='child', null=True, to='mosaic.Group')),
            ],
            options={
                'abstract': False,
            },
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
            name='Lineage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('k', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MosaicImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mosaic', models.ImageField(null=True, upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('tile_size', models.PositiveSmallIntegerField()),
                ('status', models.CharField(max_length=50, choices=[(b'pending', b'Pending'), (b'composing', b'Composing'), (b'complete', b'Complete')])),
                ('stock_tiles_hash', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='NormalizedSourceImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('tile_size', models.PositiveSmallIntegerField(choices=[(20, b'20 pixels')])),
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
            ],
            options={
                'abstract': False,
            },
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
        migrations.CreateModel(
            name='SourceImageTile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tile_image', models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to)),
                ('tile_data', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None), size=None), size=None)),
                ('status', models.CharField(max_length=50, choices=[(b'pending', b'Pending'), (b'queud', b'Queued'), (b'matching', b'Matching'), (b'matched', b'Matched')])),
                ('stock_tile_match_difference', models.PositiveIntegerField(null=True)),
                ('upper_left_x', models.PositiveIntegerField()),
                ('upper_left_y', models.PositiveIntegerField()),
                ('main_image', models.ForeignKey(related_name='all_tiles', to='mosaic.NormalizedSourceImage')),
                ('stock_tile_match', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='mosaic.NormalizedStockImage', null=True)),
            ],
            options={
                'ordering': ('upper_left_y', 'upper_left_x'),
            },
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
        migrations.CreateModel(
            name='TileGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('difference', models.PositiveIntegerField()),
                ('group', models.ForeignKey(related_name='tile_matches', to='mosaic.Group')),
                ('stockimagetile', models.ForeignKey(to='mosaic.StockImageTile')),
            ],
        ),
        migrations.AddField(
            model_name='normalizedstockimage',
            name='stock_image',
            field=models.ForeignKey(related_name='normalized_images', to='mosaic.StockImage'),
        ),
        migrations.AddField(
            model_name='normalizedsourceimage',
            name='source_image',
            field=models.ForeignKey(related_name='normalized_images', to='mosaic.SourceImage'),
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='image',
            field=models.ForeignKey(related_name='mosaic_images', to='mosaic.NormalizedSourceImage'),
        ),
        migrations.AddField(
            model_name='group',
            name='stock_tiles',
            field=models.ManyToManyField(related_name='groups', through='mosaic.TileGroup', to='mosaic.StockImageTile'),
        ),
        migrations.AddField(
            model_name='generation',
            name='lineage',
            field=models.ForeignKey(related_name='generations', to='mosaic.Lineage'),
        ),
        migrations.AlterUniqueTogether(
            name='tilegroup',
            unique_together=set([('group', 'stockimagetile')]),
        ),
        migrations.AlterUniqueTogether(
            name='sourceimagetile',
            unique_together=set([('main_image', 'upper_left_x', 'upper_left_y')]),
        ),
        migrations.AlterUniqueTogether(
            name='mosaicimage',
            unique_together=set([('image', 'tile_size', 'stock_tiles_hash')]),
        ),
        migrations.AlterUniqueTogether(
            name='generation',
            unique_together=set([('lineage', 'index')]),
        ),
    ]
