# Generated by Django 3.2.6 on 2021-12-19 00:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mood', '0029_alter_sentiment_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedMedication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_of_medication', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_deleted', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='medication_delete', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
