
"""Модели финансового учёта логистических заказов."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class FinanceRecord(models.Model):
    """Финансовые показатели отдельного заказа."""

    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="finance_record",
        verbose_name="Заказ",
    )

    fuel_price_per_liter = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Цена топлива за литр, ₸",
    )

    additional_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Дополнительные расходы, ₸",
    )

    driver_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Оплата водителю за рейс, ₸",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Примечание",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания записи",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее изменение",
    )

    class Meta:
        """Настройки отображения финансовых записей."""

        verbose_name = "Финансовая запись"
        verbose_name_plural = "Финансовые записи"
        ordering = ["-created_at"]

    def __str__(self):
        """Возвращает номер заказа для финансовой записи."""
        return f"Финансы заказа #{self.order_id}"

    def calculate_fuel_liters(self):
        """Рассчитывает количество топлива для поездки."""
        order = self.order

        if order.distance_km is None or order.vehicle_id is None:
            return Decimal("0.00")

        distance = Decimal(str(order.distance_km))
        consumption = Decimal(str(order.vehicle.fuel_consumption))

        return (
            distance * consumption / Decimal("100")
        ).quantize(Decimal("0.01"))

    def calculate_fuel_cost(self):
        """Рассчитывает стоимость топлива для поездки."""
        fuel_liters = self.calculate_fuel_liters()

        return (
            fuel_liters * self.fuel_price_per_liter
        ).quantize(Decimal("0.01"))

    def calculate_revenue(self):
        """Возвращает выручку по заказу."""
        if self.order.final_price is not None:
            return self.order.final_price

        if self.order.estimated_price is not None:
            return self.order.estimated_price

        return Decimal("0.00")

    def calculate_total_expenses(self):
        """Рассчитывает общие расходы на выполнение заказа."""
        return (
            self.calculate_fuel_cost()
            + self.additional_expenses
            + self.driver_salary
        ).quantize(Decimal("0.01"))

    def calculate_profit(self):
        """Рассчитывает прибыль до учёта прочих расходов компании."""
        return (
            self.calculate_revenue()
            - self.calculate_total_expenses()
        ).quantize(Decimal("0.01"))


class DriverSalary(models.Model):
    """Начисление зарплаты и учёт выплаты водителю."""

    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.PROTECT,
        related_name="salary_records",
        verbose_name="Водитель",
    )

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_records",
        verbose_name="Рейс",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Начислено, ₸",
    )

    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Выплачено, ₸",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Примечание",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата начисления",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее изменение",
    )

    class Meta:
        """Настройки модели начислений водителям."""

        verbose_name = "Зарплата водителя"
        verbose_name_plural = "Зарплаты водителей"
        ordering = ["-created_at"]

    def __str__(self):
        """Возвращает описание начисления."""
        return f"{self.driver} — {self.amount} ₸"

    def clean(self):
        """Проверяет корректность суммы выплаты."""
        from django.core.exceptions import ValidationError

        super().clean()

        if self.paid_amount > self.amount:
            raise ValidationError({
                "paid_amount": (
                    "Выплата не может превышать сумму начисления."
                )
            })

    @property
    def remaining_amount(self):
        """Возвращает сумму, оставшуюся к выплате."""
        return self.amount - self.paid_amount
