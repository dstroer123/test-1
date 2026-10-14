from django.urls import path

from . import views

urlpatterns = [
    path(
        "salaries/",
        views.driver_salary_dashboard,
        name="driver_salary_dashboard",
    ),
]
