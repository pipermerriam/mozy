# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import mozy.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0024_delete_mosaicimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='MosaicImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mosaic', models.ImageField(null=True, upload_to=mozy.apps.core.utils.generic_upload_to)),
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
            field=models.ForeignKey(related_name='mosaics', to='mosaic.NormalizedSourceImage'),
        ),
    ]
