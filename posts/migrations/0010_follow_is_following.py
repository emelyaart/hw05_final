# Generated by Django 2.2.6 on 2021-01-09 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20210109_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='is_following',
            field=models.BooleanField(default=False),
        ),
    ]