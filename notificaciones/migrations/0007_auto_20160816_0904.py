# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-16 09:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0006_auto_20160802_1109'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alerta',
            options={'verbose_name': 'Alerta', 'verbose_name_plural': 'Alertas'},
        ),
        migrations.AlterModelOptions(
            name='alerta_miembro',
            options={'verbose_name': 'Miembro de Alerta ', 'verbose_name_plural': 'Miembros de Alertas'},
        ),
    ]