"""
User model
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core.models import TimeStampedModel, UUIDModel
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, UUIDModel):
    """
    Custom user model with email as username
    """
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return full name"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    def get_short_name(self):
        """Return short name"""
        return self.first_name or self.email.split('@')[0]