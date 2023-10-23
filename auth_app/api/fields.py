from rest_framework import serializers

from auth_app.utils.validators import password_validator
from auth_app.utils.validators import PhoneNumberValidator

PhoneNumberField = serializers.CharField(max_length=15, validators=[PhoneNumberValidator])

PasswordField = serializers.CharField(min_length=8, validators=[password_validator])
