# Generated by Django 4.2.4 on 2023-08-11 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_teacher_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='code',
        ),
    ]
