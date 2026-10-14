from django.urls import path

from . import views

urlpatterns = [
    path("create/", views.create_order, name="create_order"),
    path("my/", views.my_orders, name="my_orders"),
    path(
    "<int:order_id>/replace-driver/",
    views.replace_order_driver,
    name="replace_order_driver",
),
    path(
        "<int:order_id>/respond/",
        views.respond_to_offer,
        name="respond_to_offer",
    ),
]