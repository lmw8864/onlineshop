# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-24 21:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_ordertransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=0, max_digits=10),
        ),
    ]
