
import json

from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from drivers.models import Driver
from vehicles.models import Vehicle

from .forms import OrderForm
from .models import Order
from .routing import RouteError, get_route
from .services import assign_vehicle, calculate_order_price


@login_required
def create_order(request):
    """Создаёт заказ и рассчитывает маршрут, время и стоимость."""
    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            try:
                route = get_route(
                    form.cleaned_data["origin"],
                    form.cleaned_data["destination"],
                )
            except RouteError as exc:
                form.add_error(None, str(exc))
            else:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.client = request.user
                    order.distance_km = route["distance_km"]
                    order.route_geometry = route["geometry"]
                    order.estimated_time_hours = route["duration_hours"]
                    
                    order.estimated_price = calculate_order_price(
                        order.distance_km,
                        order.allow_shared_cargo,
                    )
                    order.status = "calculated"
                    order.save()

                    vehicle = assign_vehicle(order)

                    if vehicle is not None:
                        order.status = "offered"
                        order.save(
                            update_fields=["status", "updated_at"]
                        )
                        messages.success(
                            request,
                            "Маршрут рассчитан. Предложение "
                            "по перевозке готово к рассмотрению.",
                        )
                    else:
                        messages.warning(
                            request,
                            "Заказ создан, но подходящая свободная "
                            "машина с водителем не найдена.",
                        )

                return redirect("my_orders")
    else:
        form = OrderForm()

    return render(
        request,
        "orders/create_order.html",
        {"form": form},
    )


@login_required
def my_orders(request):

    orders = list(
        Order.objects.filter(client=request.user)
        .select_related("company", "vehicle", "driver")
        .order_by("-created_at")
    )

    for order in orders:
        order.route_geometry_json = (
            json.dumps(order.route_geometry)
            if order.route_geometry
            else ""
        )

    return render(
        request,
        "orders/my_orders.html",
        {"orders": orders},
    )



@login_required
def respond_to_offer(request, order_id):
    """Принимает или отклоняет предложение по заказу."""
    if request.method != "POST":
        return redirect("my_orders")

    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .filter(
                id=order_id,
                client=request.user,
                status="offered",
            )
            .first()
        )

        if order is None:
            messages.error(
                request,
                "Предложение не найдено или уже обработано.",
            )
            return redirect("my_orders")

        decision = request.POST.get("decision")

        if decision == "accept":
            order.client_accepted_price = True
            order.client_accepted_time = True
            order.status = "accepted"
            order.save(
                update_fields=[
                    "client_accepted_price",
                    "client_accepted_time",
                    "status",
                    "updated_at",
                ]
            )
            messages.success(
                request,
                "Предложение принято.",
            )

        elif decision == "reject":
            if order.vehicle_id:
                vehicle = order.vehicle
                vehicle.status = "free"
                vehicle.save(update_fields=["status"])

            if order.driver_id:
                driver = order.driver
                driver.status = "free"
                driver.save(update_fields=["status"])

            order.vehicle = None
            order.driver = None
            order.status = "rejected"
            order.save(
                update_fields=[
                    "vehicle",
                    "driver",
                    "status",
                    "updated_at",
                ]
            )
            messages.info(
                request,
                "Предложение отклонено. Машина и водитель освобождены.",
            )

        else:
            messages.error(
                request,
                "Неизвестное действие.",
            )

    return redirect("my_orders")

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect

from drivers.models import Driver
from orders.models import Order


@login_required
@user_passes_test(lambda user: user.is_staff)
@transaction.atomic
def replace_order_driver(request, order_id):
    """Заменяет водителя в заказе с проверкой компании и доступности."""
    if request.method != "POST":
        return redirect("my_orders")

    order = get_object_or_404(
        Order.objects.select_for_update(),
        pk=order_id,
    )

    if not order.vehicle:
        messages.error(
            request,
            "Нельзя заменить водителя: к заказу не назначен автомобиль.",
        )
        return redirect("my_orders")

    driver_id = request.POST.get("driver_id")

    if not driver_id or not driver_id.isdigit():
        messages.error(request, "Выберите водителя.")
        return redirect("my_orders")

    driver = get_object_or_404(
        Driver.objects.select_for_update(),
        pk=int(driver_id),
    )

    if driver.company_id != order.company_id:
        messages.error(
            request,
            "Водитель должен относиться к компании заказа.",
        )
        return redirect("my_orders")

    if driver.status != "free":
        messages.error(
            request,
            "Этот водитель не свободен.",
        )
        return redirect("my_orders")

    old_driver = order.driver
    vehicle = order.vehicle

    if old_driver and old_driver.pk == driver.pk:
        messages.info(request, "Этот водитель уже назначен.")
        return redirect("my_orders")

    vehicle.driver = driver
    vehicle.save(update_fields=["driver"])

    order.driver = driver
    order.save(update_fields=["driver", "updated_at"])

    driver.status = "busy"
    driver.save(update_fields=["status"])

    if old_driver:
        from vehicles.models import Vehicle

        other_busy_vehicles = Vehicle.objects.filter(
            driver=old_driver,
            status="busy",
        ).exclude(pk=vehicle.pk)

        if not other_busy_vehicles.exists():
            old_driver.status = "free"
            old_driver.save(update_fields=["status"])

    messages.success(
        request,
        f"Водитель для заказа №{order.pk} успешно заменён.",
    )
    return redirect("my_orders")
