# Generated by Django 2.2.6 on 2019-10-27 04:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_auto_20191026_2258'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofileinfo',
            name='skills',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='post_likes', to=settings.AUTH_USER_MODEL),
        ),
    ]