from rest_framework import serializers

from auth_app.utils.validators import phone_number, password_validator

PhoneNumberField = serializers.CharField(max_length=15, validators=[phone_number])

PasswordField = serializers.CharField(min_length=8, validators=[password_validator])
