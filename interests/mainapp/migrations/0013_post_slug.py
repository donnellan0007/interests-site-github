# Generated by Django 2.2.4 on 2019-10-29 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_remove_post_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=75),
        ),
    ]
