from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from .managers import CustomUserManager
from .token_generators import generate_jwt


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Адрес электронной почты', unique=True)
    is_staff = models.BooleanField(default=False)
    refresh_token = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def access_token(self):
        return generate_jwt(self.pk)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='images/')
    phone = models.CharField(max_length=13)
    role = models.CharField(max_length=30, default='Возможный покупатель')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
