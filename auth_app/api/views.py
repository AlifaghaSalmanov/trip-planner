import datetime
import math

import pytz
from django.core.paginator import Paginator
from rest_framework import permissions
from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from auth_app.utils.validators import account_activation_token
from django.utils.encoding import force_bytes, force_str

from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import F

from auth_app.api.serializers import *
from auth_app.models import *
from auth_app.utils.utils import *
import logging
logger = logging.getLogger(__file__)

User = get_user_model()


class LoginAPIView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginUserSerializer

    @swagger_auto_schema(query_serializer=LoginUserSerializer)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            message = _("Unable to log in with provided credentials.")
            return Response({'message': message}, status=409)
        user = serializer.validated_data
        request.user = user
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        response_data = {
            'full_name': user.full_name,
            'address': user.address,
            'email': user.email,
            'token': f'Token {token}',
            'is_active': user.is_active,
            'is_master': user.is_master
        }
        return Response(response_data, status=status.HTTP_200_OK)


class UserRegisterAPIView(views.APIView):
    """
    Customer Internal Register View
    """

    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = User.objects.create(**serializer.validated_data)

        expire_time = user.send_confirmation_code()

        return Response(
            {"user": UserSerializer(instance=user).data, "expire_time": expire_time},
            status=201,
        )

class UserEditAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserEditSerializer

    # @swagger_auto_schema(query_serializer=UserEditSerializer)
    def post(self, request, format=None):
        if request.data.get('phone'):
            request.data.update({"phone_number": request.data.get('phone')})
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'message': serializer.errors}, status=400)
        data = serializer.validated_data
        user = request.user
        user.__dict__.update(**data)
        user.save()
        response_data = {
            'full_name': user.full_name,
            'email': user.email,
            'address': user.address,
            'is_active': user.is_active,
            'is_master': user.is_master
        }
        return Response(response_data, status=status.HTTP_200_OK)


class MeAPIView(views.APIView):
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(instance=user)
        return Response(serializer.data)


class ChangePasswordView(views.APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(query_serializer=ChangePasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({'message': serializer.errors}, status=400)
        password = self.request.data['new_password1']
        user = request.user
        user.set_password(password)
        user.save()
        return Response(data={'message': 'Successfully!'}, status=status.HTTP_200_OK)

 
class UserActivationView(views.APIView):
    def post(self, request):
        serializer = UserActivationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        user = User.objects.get(phone_number=data["phone_number"])
        user.is_active = True
        user.phone_verified = True
        user.save()
        token, expiry = auth_login(request, user)

        return Response(
            {
                "message": "Succesfully activated",
                "token": f"Token {token}",
                "user": UserSerializer(instance=user).data,
            }
        )

    def put(self, request):
        """
        Resend confirmation code
        """
        serializer = SendConfirmationSerilaizer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        user = User.objects.get(phone_number=data["phone_number"])
        if user.phone_verified:
            return Response({"message": "User Already activated"}, status=400)
        expire_time = user.send_confirmation_code()
        return Response({"message": "succesfully sent", "expire_time": expire_time})


