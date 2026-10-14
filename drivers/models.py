from django.db import models

from companies.models import Company


class Driver(models.Model):
    """Водитель транспортной компании."""

    STATUS_CHOICES = [
        ("free", "Свободен"),
        ("busy", "Занят"),
        ("inactive", "Неактивен"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="drivers",
        verbose_name="Компания",
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Фамилия",
    )
    phone = models.CharField(
        max_length=30,
        verbose_name="Телефон",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="free",
        verbose_name="Статус",
    )
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Зарплата",
    )

    class Meta:
        """Настройки модели водителя."""

        verbose_name = "Водитель"
        verbose_name_plural = "Водители"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        """Возвращает имя водителя."""

        return f"{self.first_name} {self.last_name}"