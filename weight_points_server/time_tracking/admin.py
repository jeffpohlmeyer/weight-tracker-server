from django.contrib import admin

from .models import Day, Week


class WeekAdmin(admin.ModelAdmin):
    readonly_fields = ("weight",)


admin.site.register(Day)
admin.site.register(Week, WeekAdmin)
