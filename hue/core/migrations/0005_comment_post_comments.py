# Generated by Django 4.2.5 on 2024-05-06 15:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_follow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.CharField(max_length=500)),
                ('content', models.TextField()),
                ('commented_at', models.DateTimeField(default=datetime.datetime.now)),
                ('username', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
