# Generated by Django 3.0.2 on 2020-02-18 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0007_auto_20200217_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hide_department',
            field=models.BooleanField(default=False),
        ),
    ]
