from .models import DriverSalary, FinanceRecord
from django.contrib import admin

from .models import FinanceRecord


@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    """Отображает финансовые показатели заказов."""

    list_display = (
        "id",
        "order",
        "get_company",
        "fuel_price_per_liter",
        "get_fuel_cost",
        "additional_expenses",
        "driver_salary",
        "get_revenue",
        "get_profit",
    )

    list_filter = ("order__company", "created_at")
    search_fields = (
        "order__id",
        "order__cargo_name",
        "order__origin",
        "order__destination",
    )
    readonly_fields = (
        "get_fuel_liters",
        "get_fuel_cost",
        "get_revenue",
        "get_total_expenses",
        "get_profit",
    )

    @admin.display(description="Компания")
    def get_company(self, obj):
        """Возвращает компанию, выполняющую заказ."""
        return obj.order.company

    @admin.display(description="Топливо, л")
    def get_fuel_liters(self, obj):
        """Показывает расчётный расход топлива."""
        return obj.calculate_fuel_liters()

    @admin.display(description="Стоимость топлива, ₸")
    def get_fuel_cost(self, obj):
        """Показывает стоимость топлива."""
        return obj.calculate_fuel_cost()

    @admin.display(description="Выручка, ₸")
    def get_revenue(self, obj):
        """Показывает выручку по заказу."""
        return obj.calculate_revenue()

    @admin.display(description="Расходы всего, ₸")
    def get_total_expenses(self, obj):
        """Показывает сумму учтённых расходов."""
        return obj.calculate_total_expenses()

    @admin.display(description="Прибыль, ₸")
    def get_profit(self, obj):
        """Показывает прибыль по заказу."""
        return obj.calculate_profit()


@admin.register(DriverSalary)
class DriverSalaryAdmin(admin.ModelAdmin):
    """Управляет начислениями и выплатами водителям."""

    list_display = (
        "id",
        "driver",
        "order",
        "amount",
        "paid_amount",
        "get_remaining_amount",
        "created_at",
    )

    list_filter = ("driver__company", "created_at")
    search_fields = (
        "driver__first_name",
        "driver__last_name",
        "order__id",
    )

    readonly_fields = ("get_remaining_amount",)

    @admin.display(description="Осталось выплатить, ₸")
    def get_remaining_amount(self, obj):
        """Показывает остаток зарплаты."""
        return obj.remaining_amount
