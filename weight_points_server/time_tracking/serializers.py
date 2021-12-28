from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from weight_points_server.utils.points_calculators import calculate_daily_points
from weight_points_server.utils.time_tracking import create_days

from .models import Day, Week


class DaySerializer(serializers.ModelSerializer):
    day_of_week = serializers.SerializerMethodField()

    @staticmethod
    def get_day_of_week(obj):
        choices = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        return choices[obj.day_of_week]

    class Meta:
        model = Day
        exclude = (
            "id",
            "week",
            "user",
        )


class WeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Week
        exclude = ("user",)


# class CreateUpdateWeekSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Week
#         # exclude = ("user",)
#         fields = "__all__"

# def __init__(self, *args, **kwargs):
#     # Get user
#     request = self.context.get("request", None)
#     if request is not None:
#         self.user = request.user
#
#     data = kwargs.get('data')
#     start_date = data.get('start_date')
#     if start_date is None:
#         data['start_date'] =
#     super(CreateUpdateWeekSerializer, self).__init__(*args, **kwargs)
#     print("kwargs", kwargs)

# def validate(self, attrs):
#     print("attrs", attrs)
#     attrs["user"] = self.user
#     return attrs

# def create(self, validated_data):
#     week = super(CreateUpdateWeekSerializer, self).create(validated_data)
#     create_days(week.start_date, week.user, week, 7)
#     return week
