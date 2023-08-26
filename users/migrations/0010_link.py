# Generated by Django 4.2.4 on 2023-08-16 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_remove_video_quiz'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iframe_url', models.URLField(max_length=500)),
                ('button_url', models.URLField(max_length=500)),
            ],
        ),
    ]
