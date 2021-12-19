from django.http.response import Http404
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Week, Day
from .serializers import WeekSerializer, DaySerializer
from weight_points_server.utils.time_tracking import backfill_weeks


class WeekViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = WeekSerializer

    def get_queryset(self):
        return Week.objects.filter(user=self.request.user)

    # def get_serializer_class(self):
    #     print("self.action", self.action)
    #     if self.action == "create":
    #         return CreateUpdateWeekSerializer
    #     if self.action == "update" or self.action == "partial_update":
    #         return CreateUpdateWeekSerializer
    #     elif self.action == "retrieve":
    #         return WeekSerializer
    #     return None

    # def create(self, request, *args, **kwargs):
    #     start_date = request.data.get("start_date")
    #     if start_date is None:
    #         start_date = timezone.now().today().date()
    #         weekday = timezone.now().today().weekday()
    #         if request.user.weigh_in_day is not None:
    #             while weekday != request.user.weigh_in_day:
    #                 start_date = start_date - timedelta(days=1)
    #                 weekday = (weekday - 1) % 7
    #         request.data.update({"start_date": start_date})
    #
    #     request.data["user"] = request.user.pk
    #     request.data["weight"] = request.user.weight
    #     return super(WeekViewSet, self).create(request, *args, **kwargs)


class DayViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    lookup_field = "date"
    serializer_class = DaySerializer

    def get_queryset(self):
        return Day.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        backfill_weeks(request.user)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                "That date is not available", status=status.HTTP_404_NOT_FOUND
            )
