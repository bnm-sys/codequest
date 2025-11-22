# accounts/forms.py
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import CustomUser

PHONE_REGEX = re.compile(
    r"^\+977\d{7,12}$"
)  # +977 followed by 7-12 digits (adjust if needed)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": "+977XXXXXXXXX"})
    )
    display_name = forms.CharField(required=False, max_length=80)
    preferred_language = forms.ChoiceField(
        choices=(("en", "English"), ("ne", "नेपाली / Nepali")),
        initial="en",
        required=False,
        label="Language",
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "display_name",
            "preferred_language",
            "email",
            "phone_number",
            "password1",
            "password2",
        )

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email", "").strip()
        phone = cleaned.get("phone_number", "").strip()

        if not email and not phone:
            raise ValidationError(
                "Provide at least a +977 phone number or a valid email address."
            )

        if phone:
            if not PHONE_REGEX.match(phone):
                raise ValidationError("Phone number must be in +977XXXXXXXXX format.")
        if email:
            # django validator will raise if invalid
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("Enter a valid email address.")

        return cleaned
