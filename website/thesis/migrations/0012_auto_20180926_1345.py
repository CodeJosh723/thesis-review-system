# Generated by Django 2.1 on 2018-09-26 07:45

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesis', '0011_auto_20180926_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researchfield',
            name='teachers',
            field=models.ManyToManyField(blank=True, limit_choices_to={'is_teacher': True}, related_name='fields', to=settings.AUTH_USER_MODEL),
        ),
    ]
