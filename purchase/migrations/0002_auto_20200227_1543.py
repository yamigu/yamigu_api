# Generated by Django 3.0.2 on 2020-02-27 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default='asdasd', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='refunded_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]