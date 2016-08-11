# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-10 16:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comuna',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('visible', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('visible', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('ordinal', models.CharField(max_length=250)),
                ('visible', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='provincia',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utilidades.Region'),
        ),
        migrations.AddField(
            model_name='comuna',
            name='provincia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utilidades.Provincia'),
        ),
    ]
