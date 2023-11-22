# Generated by Django 4.2.1 on 2023-07-14 07:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('LittleLemonAPI', '0003_remove_category_id_alter_category_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_crew',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_crew', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True),
        ),
    ]
