# Generated by Django 4.1.3 on 2022-12-20 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_transaction_total_amount_field_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='pin_code',
            field=models.IntegerField(),
        ),
    ]
