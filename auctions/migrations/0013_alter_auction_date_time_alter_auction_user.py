# Generated by Django 4.1.3 on 2022-12-12 02:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_auction_date_time_alter_auction_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='date_time',
            field=models.DateTimeField(verbose_name=datetime.datetime(2022, 12, 11, 23, 36, 46, 326737)),
        ),
        migrations.AlterField(
            model_name='auction',
            name='user',
            field=models.CharField(max_length=60),
        ),
    ]
