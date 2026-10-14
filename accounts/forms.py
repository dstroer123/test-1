
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    """Форма регистрации нового клиента."""

    email = forms.EmailField(
        required=True,
        label="Электронная почта",
    )

    class Meta:
        """Настройки полей регистрации."""

        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        """Сохраняет пользователя с указанной почтой."""

        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user
