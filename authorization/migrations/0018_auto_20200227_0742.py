# Generated by Django 3.0.2 on 2020-02-27 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0017_firebasetoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firebasetoken',
            name='value',
            field=models.CharField(max_length=2048),
        ),
    ]
