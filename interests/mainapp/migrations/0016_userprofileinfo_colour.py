# Generated by Django 2.2.4 on 2019-10-31 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_post_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofileinfo',
            name='colour',
            field=models.CharField(default='#4287f5', max_length=15),
        ),
    ]