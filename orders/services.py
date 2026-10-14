from decimal import Decimal

from django.db import transaction
from django.db.models import Case, IntegerField, Value, When

from vehicles.models import Vehicle


def find_available_vehicles(company, cargo_weight, city=None):
    """Находит свободные машины компании с подходящей грузоподъёмностью."""
    vehicles = Vehicle.objects.filter(
        company=company,
        status="free",
        is_active=True,
        capacity__gte=cargo_weight,
        driver__isnull=False,
        driver__status="free",
        driver__company=company,
    )

    if city:
        vehicles = vehicles.annotate(
            city_priority=Case(
                When(current_city__iexact=city, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("city_priority", "capacity")
    else:
        vehicles = vehicles.order_by("capacity")

    return vehicles


def calculate_trip_time(distance_km):
    """Рассчитывает приблизительное время поездки в часах."""
    distance = Decimal(str(distance_km or 0))

    if distance <= 0:
        return Decimal("0.00")

    average_speed = Decimal("70")
    return (distance / average_speed).quantize(Decimal("0.01"))


def calculate_order_price(distance_km, allow_shared_cargo=False):
    """Рассчитывает предварительную стоимость перевозки в тенге."""
    distance = Decimal(str(distance_km or 0))

    if distance <= 0:
        return Decimal("0.00")

    price_per_km = (
        Decimal("200")
        if allow_shared_cargo
        else Decimal("250")
    )

    return (distance * price_per_km).quantize(Decimal("0.01"))


@transaction.atomic
def assign_vehicle(order):
    """Назначает заказу свободную машину и её свободного водителя."""
    vehicles = find_available_vehicles(
        company=order.company,
        cargo_weight=order.cargo_weight,
        city=order.origin,
    ).select_for_update()

    vehicle = vehicles.first()

    if vehicle is None:
        return None

    driver = vehicle.driver

    # Повторно проверяем доступность перед назначением.
    if (
        vehicle.status != "free"
        or not vehicle.is_active
        or vehicle.capacity < order.cargo_weight
        or driver is None
        or driver.status != "free"
        or driver.company_id != order.company_id
    ):
        return None

    vehicle.status = "busy"
    vehicle.save(update_fields=["status"])

    driver.status = "busy"
    driver.save(update_fields=["status"])

    order.vehicle = vehicle
    order.driver = driver
    order.status = "vehicle_assigned"
    order.save(
        update_fields=[
            "vehicle",
            "driver",
            "status",
            "updated_at",
        ]
    )

    return vehicle
