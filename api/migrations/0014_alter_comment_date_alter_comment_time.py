# Generated by Django 4.2.1 on 2024-10-28 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_remove_chat_participants'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='time',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
