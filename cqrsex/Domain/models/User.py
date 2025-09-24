from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    class UserRole(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"
        SUPPLIER = "SUPPLIER", "Supplier"

    user_type = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
    )
    tenant_id = models.CharField(max_length=20, default="main")

    class Meta:
        db_table = "users"
        managed = True
