# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-15 13:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0013_invoiceitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]