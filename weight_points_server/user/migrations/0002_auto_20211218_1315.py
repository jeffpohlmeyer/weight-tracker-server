# Generated by Django 3.1.7 on 2021-12-18 18:15

from django.db import migrations, models
import weight_points_server.user.models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="weigh_in_day",
            field=models.IntegerField(
                choices=[
                    (0, "Monday"),
                    (1, "Tuesday"),
                    (2, "Wednesday"),
                    (3, "Thursday"),
                    (4, "Friday"),
                    (5, "Saturday"),
                    (6, "Sunday"),
                ],
                default=weight_points_server.user.models.set_weigh_in_day,
            ),
        ),
    ]
