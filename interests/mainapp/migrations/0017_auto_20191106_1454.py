# Generated by Django 2.2.4 on 2019-11-06 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0016_userprofileinfo_colour'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofileinfo',
            name='colour',
            field=models.CharField(default='#4287f5', max_length=500),
        ),
    ]