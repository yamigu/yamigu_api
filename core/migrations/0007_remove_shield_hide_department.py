# Generated by Django 3.0.2 on 2020-02-18 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200217_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shield',
            name='hide_department',
        ),
    ]
