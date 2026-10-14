from django.urls import path

from . import views

urlpatterns = [
    path(
        "finance/",
        views.finance_dashboard,
        name="finance_dashboard",
    ),
]
