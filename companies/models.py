from django.db import models

class Company(models.Model):
    """Транспортная компания."""

    name = models.CharField(
        max_length=150,
        verbose_name="Название компании",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Телефон",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        """Настройки модели компании."""

        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ["name"]

    def __str__(self):
        """Возвращает название компании."""
        return self.name