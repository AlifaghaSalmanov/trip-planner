from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from auth_app.api.fields import PasswordField, PhoneNumberField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class LoginUserSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(request=self.context['request'], **data)
        if not user:
            raise serializers.ValidationError({'message': _("Unable to log in with provided credentials.")})
        return user


class UserEditSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    picture = serializers.ImageField(required=False)


# class RegistrationUserSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=False)
#     phone_number = serializers.CharField(required=False)
#     full_name = serializers.CharField(required=False)
#     address = serializers.CharField(required=False)
#     password = serializers.CharField()
#
#     def validate(self, attrs):
#         if not attrs.get('email') and not attrs.get('phone_number'):
#             raise serializers.ValidationError('')
#         return attrs
#
#     @staticmethod
#     def validate_phone_number(attrs):
#         if not phone_number_validator(attrs)[0]:
#             raise serializers.ValidationError(_(phone_number_validator(attrs)[1]))
#         return attrs

class UserRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=80)
    phone_number = PhoneNumberField
    email = serializers.EmailField(required=False)
    password = PasswordField
    repeat_password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        data = super().validate(attrs)
        if data["password"] != data["repeat_password"]:
            raise serializers.ValidationError(
                {"repeat_password": "Passwords not match"}
            )
        del data["repeat_password"]
        return data

    def validate_full_name(self, data):
        words = data.split()
        if len(words) != 2:
            raise serializers.ValidationError("Incorrect full name")
        return data

    def validate_phone_number(self, data):
        if User.objects.filter(phone_number=data).exists():
            raise serializers.ValidationError("This phone number already registered")
        return data

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError("This email already registered")
        data.lower()
        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        user = authenticate(request=self.context['request'], **{"email": self.context['request'].user.email,
                                                                "password": data['current_password']
                                                                })
        if not user:
            raise serializers.ValidationError({'current_password': _("Password is not valid!")})
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        # password_validation.validate_password(data['new_password1'], self.context['request'].user)
        if not self.context['request'].user:
            raise serializers.ValidationError(_("User not found!"))
        return data


class ConfirmationSerializer(serializers.Serializer):
    phone_number = PhoneNumberField
    code = serializers.CharField(max_length=6)

    queryset = User.objects.all()

    def validate(self, attrs):
        data = super().validate(attrs)
        user = User.objects.get(phone_number=data["phone"])
        if not user.check_confirmation_code(data["code"]):
            raise serializers.ValidationError({"code": "Code is invalid"})
        return data

    def validate_phone_number(self, data):
        if not self.queryset.filter(phone_number=data).exists():
            raise serializers.ValidationError("User not found")
        return data


class UserActivationSerializer(ConfirmationSerializer):
    queryset = User.objects.filter(phone_verified=False)


class SendConfirmationSerilaizer(serializers.Serializer):
    phone_number = PhoneNumberField

    def validate_phone_number(self, data):
        user = User.objects.filter(phone_number=data).first()
        if not user:
            raise serializers.ValidationError("User not found")

        if not user.is_availabe_confirmation_code():
            raise serializers.ValidationError("Confirmation code already sent")
        return data