# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mosaic', '0004_auto_20150424_1401'),
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
                ('parent', models.OneToOneField(related_name='child', to='mosaic.Group')),
                ('stock_tiles', models.ManyToManyField(related_name='groups', to='mosaic.StockImageTile')),
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
        migrations.AddField(
            model_name='generation',
            name='lineage',
            field=models.ForeignKey(related_name='generations', to='mosaic.Lineage'),
        ),
        migrations.AlterUniqueTogether(
            name='generation',
            unique_together=set([('lineage', 'index')]),
        ),
    ]
