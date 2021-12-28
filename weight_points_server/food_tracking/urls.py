from rest_framework.routers import DefaultRouter

from .views import FoodInstanceViewSet, MealViewSet

router = DefaultRouter()
router.register("meal", MealViewSet, basename="meal")
router.register("food-instance", FoodInstanceViewSet, basename="food-instance")
