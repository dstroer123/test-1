from django.db import models

from companies.models import Company
from drivers.models import Driver


class Vehicle(models.Model):
    """Автомобиль транспортной компании."""

    STATUS_CHOICES = [
        ("free", "Свободен"),
        ("busy", "Занят"),
        ("repair", "На ремонте"),
        ("inactive", "Неактивен"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="vehicles",
        verbose_name="Компания",
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicles",
        verbose_name="Водитель",
    )
    brand = models.CharField(
        max_length=100,
        verbose_name="Марка",
    )
    model = models.CharField(
        max_length=100,
        verbose_name="Модель",
    )
    plate_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Госномер",
    )
    capacity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Грузоподъёмность, тонн",
    )
    fuel_consumption = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Расход, л/100 км",
    )
    current_city = models.CharField(
        max_length=100,
        verbose_name="Текущий город",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="free",
        verbose_name="Статус",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    class Meta:
        """Настройки модели автомобиля."""

        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["brand", "model"]

    def __str__(self):
        """Возвращает название автомобиля и госномер."""

        return f"{self.brand} {self.model} — {self.plate_number}"