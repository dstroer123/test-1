
from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    """Форма создания заказа на перевозку."""

    class Meta:
        """Настройки полей формы."""

        model = Order

        fields = [
            "company",
            "cargo_name",
            "cargo_type",
            "cargo_weight",
            "origin",
            "destination",
            "allow_shared_cargo",
        ]

        widgets = {
            "cargo_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "cargo_type": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "cargo_weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "origin": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "destination": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "company": forms.Select(
                attrs={"class": "form-select"}
            ),
        }
