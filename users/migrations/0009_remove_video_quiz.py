# Generated by Django 4.2.4 on 2023-08-14 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_video_quiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='quiz',
        ),
    ]
