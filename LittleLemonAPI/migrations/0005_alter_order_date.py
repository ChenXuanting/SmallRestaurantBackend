# Generated by Django 4.2.1 on 2023-07-14 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0004_alter_order_delivery_crew_alter_order_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
