from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import FoodInstance, Meal
from .serializers import FoodInstanceSerializer, MealSerializer, MealUpdateSerializer


class MealViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return MealUpdateSerializer
        return MealSerializer


class FoodInstanceViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = FoodInstanceSerializer

    def get_queryset(self):
        return FoodInstance.objects.filter(user=self.request.user)
