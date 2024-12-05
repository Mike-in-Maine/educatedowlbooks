from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
