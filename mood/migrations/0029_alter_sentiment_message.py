# Generated by Django 3.2.6 on 2021-12-18 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood', '0028_auto_20211217_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentiment',
            name='message',
            field=models.TextField(max_length=280),
        ),
    ]
