# Generated by Django 3.0.2 on 2020-02-14 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200214_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedimage',
            name='feed',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='core.Feed'),
        ),
    ]
