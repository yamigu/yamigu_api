# Generated by Django 3.0.2 on 2020-02-22 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0013_identityverification_created_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_student',
        ),
        migrations.AddField(
            model_name='belongverification',
            name='is_student',
            field=models.BooleanField(default=True),
        ),
    ]