# Generated by Django 3.2.6 on 2021-11-27 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentiment',
            name='personal_rating',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
