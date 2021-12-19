from rest_framework.routers import DefaultRouter

from .views import WeekViewSet, DayViewSet

router = DefaultRouter()
router.register("week", WeekViewSet, basename="week")
router.register("day", DayViewSet, basename="day")
