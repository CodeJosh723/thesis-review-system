# Generated by Django 3.0.7 on 2020-07-14 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0002_auto_20200713_2253'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentgroup',
            options={'ordering': ['id']},
        ),
    ]
