from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from weight_points_server.time_tracking.models import Week, Day
from weight_points_server.utils.points_calculators import calculate_daily_points

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)

    def update(self, instance, validated_data):
        data = super(UserSerializer, self).update(instance, validated_data)

        if "weight" in validated_data.keys():
            today = timezone.now().today().date()
            weekday = timezone.now().today().weekday()
            # If you're updating your weight on the weigh-in day
            # or if you've not yet input your weight
            # then your daily point total should update
            curr_week = Week.objects.filter(user=instance).last()
            if weekday == instance.weigh_in_day or (
                curr_week is not None and not curr_week.weight_recorded
            ):
                Week.objects.filter(user=instance, start_date=today).update(
                    weight=validated_data.get("weight")
                )
                daily_points = calculate_daily_points(instance)
                qs = Day.objects.filter(user=instance, date__gte=today)
                for item in qs:
                    item.weight = validated_data.get("weight")
                    item.total_points = daily_points
                    item.points_remaining = daily_points - item.points_used
                Day.objects.bulk_update(
                    qs, ["weight", "total_points", "points_remaining"]
                )
            # Your weight for subsequent days should update as well for visibility
            else:
                Day.objects.filter(user=instance, date__gte=today).update(
                    weight=validated_data.get("weight")
                )
            curr_week.weight_recorded = True
            curr_week.save()
        return data
