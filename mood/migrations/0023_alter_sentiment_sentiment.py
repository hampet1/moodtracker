# Generated by Django 3.2.6 on 2021-11-28 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood', '0022_alter_sentiment_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentiment',
            name='sentiment',
            field=models.IntegerField(null=True),
        ),
    ]
