from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройки отображения заказов."""

    list_display = (
        "id",
        "client",
        "company",
        "cargo_name",
        "cargo_weight",
        "origin",
        "destination",
        "vehicle",
        "driver",
        "estimated_price",
        "final_price",
        "status",
        "allow_shared_cargo",
        "created_at",
    )

    list_filter = (
        "status",
        "company",
        "allow_shared_cargo",
        "client_accepted_price",
        "client_accepted_time",
        "created_at",
    )

    search_fields = (
        "cargo_name",
        "cargo_type",
        "origin",
        "destination",
        "client__username",
        "company__name",
        "vehicle__plate_number",
        "driver__first_name",
        "driver__last_name",
    )

    list_editable = (
        "status",
    )