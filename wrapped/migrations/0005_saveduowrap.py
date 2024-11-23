# Generated by Django 5.1.1 on 2024-11-22 21:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wrapped', '0004_rename_favoritewrap_savewrap'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SaveDuoWrap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user1_data', models.JSONField()),
                ('user2_data', models.JSONField()),
                ('compatibility', models.FloatField()),
                ('valence_user1', models.FloatField()),
                ('valence_user2', models.FloatField()),
                ('top_tracks_user1', models.JSONField()),
                ('top_tracks_user2', models.JSONField()),
                ('interleaved_preview_urls', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]