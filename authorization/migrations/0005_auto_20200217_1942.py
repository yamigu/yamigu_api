# Generated by Django 3.0.2 on 2020-02-17 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0004_auto_20200217_1729'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bvimage',
            old_name='image',
            new_name='data',
        ),
        migrations.RenameField(
            model_name='profileimage',
            old_name='image',
            new_name='data',
        ),
    ]
