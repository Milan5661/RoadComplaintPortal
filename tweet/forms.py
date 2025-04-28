from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from .models import Complaint, AdminProfile
import re

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["description", "image", "latitude", "longitude", "address"]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

class UserRegistrationForm(forms.Form):
    email = forms.EmailField(validators=[EmailValidator()])
    password = forms.CharField(
        widget=forms.PasswordInput(),
        min_length=6,
        help_text="Password must be at least 6 characters."
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the email domain is Gmail
        if not re.match(r'^[a-zA-Z0-9_.+-]+@gmail\.com$', email):
            raise ValidationError("Please enter a valid Gmail address.")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password


class AdminSecurityQuestionForm(forms.Form):
    answer1 = forms.CharField(
        label="What is your favourite food?",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        max_length=100,
    )
    answer2 = forms.CharField(
        label="What is your childhood name?",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        max_length=100,
    )

class AdminPasswordResetForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    answer1 = forms.CharField(
        label="What is your favourite food?",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        max_length=100,
    )
    answer2 = forms.CharField(
        label="What is your childhood name?",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        max_length=100,
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(),
        min_length=6,
        help_text="Password must be at least 6 characters."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(),
        min_length=6,
        help_text="Enter the same password as before, for verification."
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            raise ValidationError("New password and Confirm password do not match.")
        return cleaned_data
