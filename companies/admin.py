from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Настройки отображения компаний в админ-панели."""

    list_display = (
        "name",
        "city",
        "phone",
        "email",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "city",
    )
    search_fields = (
        "name",
        "city",
        "email",
    )