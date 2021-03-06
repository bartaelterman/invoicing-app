# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 20:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0006_invoice_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='days',
            field=models.DecimalField(decimal_places=2, default=2, max_digits=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='end',
            field=models.DateField(default=datetime.date(2017, 5, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='invoice',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='start',
            field=models.DateField(default=datetime.date(2017, 4, 1)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='number',
            field=models.IntegerField(editable=False, unique=True),
        ),
    ]
