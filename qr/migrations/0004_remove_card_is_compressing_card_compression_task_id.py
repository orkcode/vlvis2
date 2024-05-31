# Generated by Django 5.0.6 on 2024-05-29 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qr', '0003_alter_card_is_compressing'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='is_compressing',
        ),
        migrations.AddField(
            model_name='card',
            name='compression_task_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
