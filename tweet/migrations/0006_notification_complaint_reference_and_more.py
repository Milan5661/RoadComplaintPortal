# Generated by Django 5.2.1 on 2025-05-31 12:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0005_alter_notification_notification_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='complaint_reference',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='complaint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='tweet.complaint'),
        ),
    ]
