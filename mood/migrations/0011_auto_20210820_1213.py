# Generated by Django 3.2.6 on 2021-08-20 02:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mood', '0010_auto_20210820_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='medication',
            name='user',
            field=models.ManyToManyField(blank=True, related_name='medication', to=settings.AUTH_USER_MODEL),
        ),
    ]
