# Generated by Django 3.0.2 on 2020-02-17 08:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_management', '0001_initial'),
        ('authorization', '0003_auto_20200214_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='num_of_free',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='bvimage',
            name='bv',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='authorization.BelongVerification'),
        ),
        migrations.AlterField(
            model_name='bvimage',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bv', to='file_management.Image'),
        ),
        migrations.AlterField(
            model_name='profileimage',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='file_management.Image'),
        ),
    ]
