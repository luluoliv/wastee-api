# Generated by Django 4.2.1 on 2024-10-23 00:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_remove_seller_address_seller_birth_date_seller_cpf_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_as_buyer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chat',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chats_as_seller', to='api.seller'),
        ),
    ]