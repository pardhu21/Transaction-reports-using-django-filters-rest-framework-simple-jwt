# Generated by Django 4.1.3 on 2022-12-20 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_customer_pin_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='total_amount',
            field=models.IntegerField(blank=True, editable=False),
        ),
    ]
