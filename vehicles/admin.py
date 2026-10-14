from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Настройки отображения автомобилей."""

    list_display = (
        "brand",
        "model",
        "plate_number",
        "company",
        "driver",
        "capacity",
        "current_city",
        "status",
    )
    list_filter = (
        "company",
        "status",
        "current_city",
    )
    search_fields = (
        "brand",
        "model",
        "plate_number",
        "current_city",
    )