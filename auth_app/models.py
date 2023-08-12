from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from auth_app.utils.utils import get_user_profile_pic_path, make_random_code
from core.models import GenericModel, ExtraDataModelMixin
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMessage
from datetime import timedelta

from core.utils.utils import SMS


# from django.utils.translation import gettext_lazy as _
# from PIL import Image
# from django.contrib.postgres.fields import JSONField

# Create your models here.
class MyUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True, null=True)
    phone_number = models.CharField(max_length=30, unique=True, null=True)
    full_name = models.CharField('Full name', max_length=255, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    is_staff = models.BooleanField('staff status', default=False,
                                   help_text='Designates whether the user can log into this admin '
                                               'site.')
    is_active = models.BooleanField('active', default=False,
                                    help_text='Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.')
    is_admin = models.BooleanField('Admin status', default=False)
    is_master = models.BooleanField('Is Master', default=False)
    phone_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date joined")

    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        if self.full_name:
            return self.full_name
        return "{}".format(self.email)

    def check_confirmation_code(self, input_code: str) -> bool:
        cr = timezone.now() - timedelta(seconds=settings.OTP_INTERVAL)
        code = self.codes.filter(
            is_active=True, created_at__gt=cr, code=input_code
        ).first()
        if code:
            code.is_active = False
            code.save()
            return True
        return False

    def send_confirmation_code(self, type: str = "sms"):
        random_code = make_random_code()
        code = self.codes.create(code=random_code)
        expire_time = code.created_at + timedelta(seconds=settings.OTP_INTERVAL)
        if type == "sms":
            r = SMS.send(self.phone_number, random_code)
        elif type == "email":
            msg = EmailMessage(
                "Trip Planner Confirmation code", str(random_code), to=[self.email]
            )
            msg.send()
        return expire_time


class UserProfile(GenericModel, ExtraDataModelMixin):
    GENDER_CHOICES = (("F", "Female"), ("M", "Male"))

    ORIGIN_CHOICES = (
        ("G", "Google"),
        ("L", "Linkedin"),
        ("A", "Apple"),
        ("I", "Internal"),
    )

    user = models.OneToOneField(
        "auth_app.CustomUser", on_delete=models.CASCADE, related_name="profile"
    )

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True
    )
    interests = models.ManyToManyField("auth_app.UserInterests")
    job_title = models.CharField(max_length=100, null=True, blank=True)
    identificator = models.CharField(max_length=10, null=True, blank=True)
    profile_pic = models.ImageField(
        upload_to=get_user_profile_pic_path, null=True, blank=True
    )
    origin = models.CharField(max_length=1, null=True, blank=True, choices=ORIGIN_CHOICES, default="G")
    # subscription = models.OneToOneField(
    #     "subscription.Subscription",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="customer",
    # )

    def __str__(self) -> str:
        return f"{self.user.id} {self.user.full_name} User Profile"


class UserInterests(ExtraDataModelMixin):
    """
        Objects will be created by CaspianSoft.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"


class ConfirmationCode(GenericModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)


