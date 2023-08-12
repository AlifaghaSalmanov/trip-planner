from django.utils import timezone
from random import randint
from django.contrib.auth.signals import user_logged_in

from rest_framework.serializers import DateTimeField

from knox.models import AuthToken
from knox.settings import knox_settings


def auth_login(request, user):
    instance, token = AuthToken.objects.create(user)
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    datetime_format = knox_settings.EXPIRY_DATETIME_FORMAT

    expiry = DateTimeField(format=datetime_format).to_representation(instance.expiry)
    token = token
    return token, expiry


def get_user_profile_pic_path(instance, filename):
    return f'users/{instance.user.id}/{timezone.now().date().strftime("%Y-%m-%d")}-{filename}'


def make_random_code():
    return randint(100000, 999999)