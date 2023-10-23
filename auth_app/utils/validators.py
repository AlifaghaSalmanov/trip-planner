import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from rest_framework import serializers


class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))


account_activation_token = AppTokenGenerator()

@deconstructible
class PhoneNumberValidator(validators.RegexValidator):
    regex = r'^\+?[0-9]{9,15}$'
    message = _(
        'Phone number is invalid. This may contain only digits. Allowed length is 9 - 15'
    )
    flags = 0


def password_validator(data):
    if all(not c.isupper() for c in data):
        raise serializers.ValidationError("Upper character is required")
    if all(not c.islower() for c in data):
        raise serializers.ValidationError("Lower character is required")
    if all(not c.isdigit() for c in data):
        raise serializers.ValidationError("Number character is required")
    if data.isdigit():
        raise serializers.ValidationError("Not only number")
    if data.isalnum():
        raise serializers.ValidationError("Symbol character is required")


def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if (re.match(regex, email)):
        return True
    return False