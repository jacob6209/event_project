from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class CustomUser(AbstractUser):
    # national_id=models.CharField(max_length=20, unique=True)
    department=models.CharField(max_length=20)
    phone=models.CharField(max_length=11)