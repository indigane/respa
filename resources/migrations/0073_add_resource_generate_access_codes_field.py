# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-17 08:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0072_reservable_min_and_max_days_verbose_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='generate_access_codes',
            field=models.BooleanField(default=True, editable=False, help_text='Should access codes generated by the general system', verbose_name='Generate access codes'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='state',
            field=models.CharField(choices=[('created', 'created'), ('cancelled', 'cancelled'), ('confirmed', 'confirmed'), ('denied', 'denied'), ('requested', 'requested')], default='created', max_length=16, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='access_code_type',
            field=models.CharField(choices=[('none', 'None'), ('pin4', '4-digit PIN code'), ('pin6', '6-digit PIN code')], default='none', max_length=20, verbose_name='Access code type'),
        ),
    ]