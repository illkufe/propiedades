# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-28 16:26
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
                ('descripcion', models.TextField(blank=True)),
                ('fecha', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('creado_en', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Alerta_Miembro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.DateField()),
                ('alerta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notificaciones.Alerta')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='alerta',
            name='miembros',
            field=models.ManyToManyField(through='notificaciones.Alerta_Miembro', to=settings.AUTH_USER_MODEL),
        ),
    ]