# Generated by Django 3.2.6 on 2021-11-27 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mood', '0020_alter_sentiment_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentiment',
            name='rating',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
