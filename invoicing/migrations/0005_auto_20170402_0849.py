# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-02 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0004_project_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='invoice_template',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='timesheet_template',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
