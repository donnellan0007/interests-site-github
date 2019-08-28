# Generated by Django 2.2.4 on 2019-08-20 13:17

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0008_auto_20190820_2025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={},
        ),
        migrations.RenameField(
            model_name='post',
            old_name='content',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='post',
            name='created_on',
        ),
        migrations.RemoveField(
            model_name='post',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='post',
            name='status',
        ),
        migrations.RemoveField(
            model_name='post',
            name='updated_on',
        ),
        migrations.AddField(
            model_name='post',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='post',
            name='published_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=60),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=25)),
                ('text', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved_comment', models.BooleanField(default=False)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='mainapp.Post')),
            ],
        ),
    ]
