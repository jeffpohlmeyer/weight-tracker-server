# Generated by Django 3.1.7 on 2021-12-18 20:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("time_tracking", "0006_day_weight"),
    ]

    operations = [
        migrations.RenameField(
            model_name="week",
            old_name="points_remaining",
            new_name="weekly_points_remaining",
        ),
        migrations.RenameField(
            model_name="week",
            old_name="points_used",
            new_name="weekly_points_used",
        ),
        migrations.RenameField(
            model_name="week",
            old_name="total_points",
            new_name="weekly_total_points",
        ),
    ]
