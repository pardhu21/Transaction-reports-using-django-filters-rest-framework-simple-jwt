# Generated by Django 4.1.3 on 2022-12-24 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_rename_timestamp_gt_filter_timestamp_greater_than_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
