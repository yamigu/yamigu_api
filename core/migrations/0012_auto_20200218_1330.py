# Generated by Django 3.0.2 on 2020-02-18 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20200218_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='requested_on',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
