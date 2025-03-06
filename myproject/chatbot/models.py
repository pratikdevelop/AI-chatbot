from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
import json

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.CharField(max_length=120, null=True, blank=True)
    preferences = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'phone']

    def set_preferences(self, preferences_dict):
        self.preferences = json.dumps(preferences_dict)

    def get_preferences(self):
        return json.loads(self.preferences) if self.preferences else {}

    def __str__(self):
        return self.username

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"