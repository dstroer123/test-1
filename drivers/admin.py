from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """Настройки отображения водителей."""

    list_display = (
        "first_name",
        "last_name",
        "company",
        "phone",
        "status",
        "salary",
    )
    list_filter = (
        "company",
        "status",
    )
    search_fields = (
        "first_name",
        "last_name",
        "phone",
    )