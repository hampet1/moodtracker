# Generated by Django 3.2.6 on 2021-11-27 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood', '0016_merge_20211127_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentiment',
            name='rating',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
