# Generated by Django 3.0.7 on 2020-08-02 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0010_auto_20200731_1428'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username']},
        ),
    ]