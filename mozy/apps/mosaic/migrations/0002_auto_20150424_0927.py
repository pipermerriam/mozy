# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mozy.apps.core.utils


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    MosaicImage = apps.get_model("mosaic", "MosaicImage")
    MosaicImage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0001_squashed_0026_auto_20150414_1819'),
    ]

    operations = [
        migrations.RunPython(
            forwards_func,
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='status',
            field=models.CharField(default='complete', max_length=50, choices=[(b'pending', b'Pending'), (b'composing', b'Composing'), (b'complete', b'Complete')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mosaicimage',
            name='stock_tiles_hash',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sourceimagetile',
            name='tile_image',
            field=models.ImageField(upload_to=mozy.apps.core.utils.uuid_upload_to),
        ),
        migrations.AlterField(
            model_name='sourceimagetile',
            name='upper_left_x',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='sourceimagetile',
            name='upper_left_y',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='mosaicimage',
            unique_together=set([('image', 'tile_size', 'stock_tiles_hash')]),
        ),
    ]
