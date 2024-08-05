from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.


class AppUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), blank=True)
