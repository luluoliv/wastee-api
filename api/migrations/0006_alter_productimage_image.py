# Generated by Django 4.2.1 on 2024-10-08 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_productimage_image_url_productimage_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.URLField(default='https://example.com/default-image.jpg'),
        ),
    ]
