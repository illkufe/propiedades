# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-28 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notificaciones', '0004_auto_20160728_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerta_miembro',
            name='estado',
            field=models.BooleanField(default=True),
        ),
    ]
