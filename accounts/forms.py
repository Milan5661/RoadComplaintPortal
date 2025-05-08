from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from tweet.models import Complaint, AdminProfile  # Ensure these models are used correctly
import re

# ComplaintForm (ModelForm)
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["description", "latitude", "longitude", "address"]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        images = self.files.getlist('images') if hasattr(self, 'files') else []
        if len(images) > 4:
            raise ValidationError('You can upload a maximum of 4 images per complaint.')
        return cleaned_data

# UserRegistrationForm (Form)
class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, help_text="Pick a unique username.")
    email = forms.EmailField(validators=[EmailValidator()])
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        max_length=15,
        help_text="Password must be 8-15 characters, include a number, an uppercase and a lowercase letter."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        max_length=15,
        help_text="Re-enter your password."
    )
    security_answer_1 = forms.CharField(max_length=100, required=True, label="What is your favourite food?")
    security_answer_2 = forms.CharField(max_length=100, required=True, label="What is your childhood name?")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.match(r'^[a-zA-Z0-9_.+-]+@gmail\.com$', email):
            raise ValidationError("Please enter a valid Gmail address.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        errors = []
        if not password:
            errors.append("Password is required.")
        if password:
            if len(password) < 8 or len(password) > 15:
                errors.append("Password must be between 8 and 15 characters long.")
            if not re.search(r'[A-Z]', password):
                errors.append("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                errors.append("Password must contain at least one lowercase letter.")
            if not re.search(r'\d', password):
                errors.append("Password must contain at least one number.")
        if errors:
            raise ValidationError(errors)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


# AdminSecurityQuestionForm (Form)
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

# UserPasswordResetForm (Form)
class UserPasswordResetForm(forms.Form):
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
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

# AdminPasswordResetForm (Form)
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
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
