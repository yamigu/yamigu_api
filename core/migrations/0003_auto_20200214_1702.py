# Generated by Django 3.0.2 on 2020-02-14 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200213_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='before',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next', to='core.Feed'),
        ),
    ]
