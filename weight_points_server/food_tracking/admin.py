from django.contrib import admin

from .models import Food, FoodInstance, Meal


class MealAdmin(admin.ModelAdmin):
    readonly_fields = ("points",)


admin.site.register(Meal, MealAdmin)
admin.site.register(Food)
admin.site.register(FoodInstance)
