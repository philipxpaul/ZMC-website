# Generated by Django 4.2.4 on 2023-08-14 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
        ('users', '0007_remove_teacher_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='quiz',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.quiz'),
        ),
    ]