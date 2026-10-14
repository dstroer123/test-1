from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from companies.models import Company
from drivers.models import Driver
from vehicles.models import Vehicle


class Order(models.Model):
    """Заказ на перевозку груза."""

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("calculated", "Стоимость рассчитана"),
        ("offered", "Предложение отправлено"),
        ("accepted", "Принят"),
        ("rejected", "Отклонён"),
        ("vehicle_assigned", "Машина назначена"),
        ("driver_assigned", "Водитель назначен"),
        ("loading", "Погрузка"),
        ("loaded", "Погружен"),
        ("in_transit", "В пути"),
        ("arrived", "Прибыл"),
        ("completed", "Завершён"),
        ("cancelled", "Отменён"),
    ]

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Клиент",
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Транспортная компания",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Автомобиль",
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Водитель",
    )

    cargo_name = models.CharField(
        max_length=200,
        verbose_name="Название груза",
    )

    cargo_type = models.CharField(
        max_length=100,
        verbose_name="Тип груза",
    )

    cargo_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Вес груза, тонн",
    )

    origin = models.CharField(
        max_length=200,
        verbose_name="Место загрузки",
    )

    destination = models.CharField(
        max_length=200,
        verbose_name="Место доставки",
    )

    route_geometry = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Геометрия маршрута",
    )

    distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Расстояние, км",
    )

    estimated_time_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Расчётное время, часов",
    )

    estimated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Предварительная стоимость",
    )

    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Итоговая стоимость",
    )

    allow_shared_cargo = models.BooleanField(
        default=False,
        verbose_name="Разрешить попутный груз",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
    )

    client_accepted_price = models.BooleanField(
        default=False,
        verbose_name="Клиент принял стоимость",
    )

    client_accepted_time = models.BooleanField(
        default=False,
        verbose_name="Клиент принял время",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее изменение",
    )

    class Meta:
        """Настройки отображения и сортировки заказов."""

        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        """Возвращает краткое описание заказа."""
        return (
            f"Заказ #{self.id}: "
            f"{self.origin} → {self.destination}"
        )

    def clean(self):
        """Проверяет соответствие автомобиля и водителя заказу."""
        super().clean()

        if self.vehicle_id and self.company_id:
            if self.vehicle.company_id != self.company_id:
                raise ValidationError({
                    "vehicle": (
                        "Автомобиль должен принадлежать "
                        "выбранной транспортной компании."
                    )
                })

            if self.vehicle.capacity < self.cargo_weight:
                raise ValidationError({
                    "vehicle": (
                        "Груз превышает грузоподъёмность автомобиля."
                    )
                })

        if self.driver_id and self.company_id:
            if self.driver.company_id != self.company_id:
                raise ValidationError({
                    "driver": (
                        "Водитель должен относиться "
                        "к выбранной транспортной компании."
                    )
                })

    def calculate_price(self):
        """Рассчитывает стоимость перевозки по километражу."""
        if self.distance_km is None or self.vehicle is None:
            return 0

        price_per_km = 200 if self.allow_shared_cargo else 250

        return float(self.distance_km) * price_per_km

    def can_assign_vehicle(self):
        """Проверяет достаточность грузоподъёмности автомобиля."""
        if not self.vehicle:
            return False

        return self.vehicle.capacity >= self.cargo_weight
