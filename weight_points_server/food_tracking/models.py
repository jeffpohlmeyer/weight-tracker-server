from django.conf import settings
from django.db import models

from weight_points_server.time_tracking.models import Day


class Meal(models.Model):
    MEAL_CHOICES = [(0, "Breakfast"), (1, "Lunch"), (2, "Dinner"), (3, "Anytime")]

    name = models.IntegerField(choices=MEAL_CHOICES, default=3)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return (
            f"User: {self.user}, date: {self.day.date}, meal: {self.get_name_display()}"
        )


class Food(models.Model):
    class ServingUnit(models.TextChoices):
        KG = "KG", "kg"
        GM = "GM", "g"
        OZ = "OZ", "oz"
        LB = "LB", "lb"
        TSP = "TSP", "tsp"
        TBSP = "TBSP", "tbsp"
        FLOZ = "FLOZ", "fl oz"
        CUP = "CUP", "cup"
        ML = "ML", "ml"
        L = "L", "l"
        EACH = "EACH", "each"

    name = models.CharField(max_length=128)
    fat = models.FloatField()
    carbs = models.FloatField()
    fiber = models.FloatField()
    protein = models.FloatField()
    serving_size = models.FloatField()
    serving_unit = models.CharField(choices=ServingUnit.choices, max_length=32)
    # serving_unit = models.CharField(max_length=32)

    user_created = models.BooleanField(default=True)
    notes = models.CharField(max_length=256, null=True, blank=True)
    # recipe = models.ForeignKey(Recipe, on_delete=models.DO_NOTHING, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True
    )

    def __str__(self):
        return self.name


class FoodInstance(models.Model):
    quantity = models.FloatField()
    quantity_string = models.CharField(max_length=16)
    points = models.IntegerField(null=True, blank=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    meal = models.ManyToManyField(Meal)
