# Generated by Django 4.2.4 on 2024-04-23 09:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("BrowseRecord", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="browserecord",
            name="article_id",
            field=models.CharField(max_length=512),
        ),
    ]