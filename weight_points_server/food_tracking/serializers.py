from django.db.models import Sum
from rest_framework import serializers

from weight_points_server.time_tracking.models import Day

from .models import FoodInstance, Meal, Food
from weight_points_server.utils.points_calculators import calculate_food_points


def update_daily_points(day):
    meal_ids = Meal.objects.filter(day=day).values_list("id")
    points = FoodInstance.objects.filter(meal_id__in=meal_ids).aggregate(Sum("points"))[
        "points__sum"
    ]
    points_remaining = day.total_points - points
    day.points_used = points
    day.points_remaining = points_remaining
    day.save()
    if points_remaining < 0:
        weekly_points_used = Day.objects.filter(
            week=day.week, points_remaining__lt=0
        ).aggregate(Sum("points_remaining"))["points_remaining__sum"]
        week = day.week
        week.weekly_points_used = -weekly_points_used
        week.weekly_points_remaining = week.weekly_total_points + weekly_points_used
        week.save()


class FoodInstanceSerializer(serializers.ModelSerializer):
    food = serializers.CharField()

    class Meta:
        model = FoodInstance
        exclude = ("meal",)


class MealSerializer(serializers.ModelSerializer):
    foodinstance_set = FoodInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Meal
        fields = (
            "get_name_display",
            "foodinstance_set",
        )


class FoodInstanceInputSerializer(serializers.ModelSerializer):
    food = serializers.PrimaryKeyRelatedField(read_only=True)
    meal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FoodInstance
        exclude = ("points",)

    def create(self, validated_data):
        food_instance = super(FoodInstanceInputSerializer, self).create(validated_data)
        update_daily_points(food_instance.meal.day)


class MealUpdateSerializer(serializers.ModelSerializer):
    food = FoodInstanceInputSerializer()
    removed = serializers.BooleanField(default=False)

    class Meta:
        model = Meal
        fields = (
            "food",
            "removed",
        )

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        self.food_pk = None
        food_dict = data.get("food")
        if food_dict is not None:
            self.food_pk = food_dict.get("food")
        super(MealUpdateSerializer, self).__init__(*args, **kwargs)

    def validate(self, attrs):
        attrs["food_pk"] = self.food_pk
        return attrs

    def update(self, instance, validated_data):
        food = validated_data.get("food")
        food_pk = validated_data.get("food_pk")
        quantity = food.get("quantity")
        quantity_string = food.get("quantity_string")
        food_instance, _ = FoodInstance.objects.get_or_create(
            quantity=quantity,
            quantity_string=quantity_string,
            food_id=food_pk,
        )
        points = calculate_food_points(
            Food.objects.get(id=food_pk), quantity, quantity_string
        )
        food_instance.points = points
        food_instance.save()
        food_instance.meal.add(instance)
        meal_points = instance.foodinstance_set.aggregate(Sum("points"))["points__sum"]
        if validated_data.get("removed"):
            meal_points -= points
        else:
            meal_points += points
        meal = super(MealUpdateSerializer, self).update(
            instance, {**validated_data, "points": meal_points}
        )
        update_daily_points(meal.day)
        return meal
