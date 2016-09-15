# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-12 12:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alerta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('descripcion', models.TextField()),
                ('fecha', models.DateTimeField()),
                ('visible', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now=True)),
                ('creador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creador', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Alertas',
                'verbose_name': 'Alerta',
            },
        ),
        migrations.CreateModel(
            name='Alerta_Miembro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('alerta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notificaciones.Alerta')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Miembros de Alertas',
                'verbose_name': 'Miembro de Alerta ',
            },
        ),
        migrations.AddField(
            model_name='alerta',
            name='miembros',
            field=models.ManyToManyField(through='notificaciones.Alerta_Miembro', to=settings.AUTH_USER_MODEL),
        ),
    ]
