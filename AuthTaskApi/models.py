from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUserModel(AbstractUser):
    is_delete = models.BooleanField(default=False)


class DataOperationModel(models.Model):
    user = models.ForeignKey(
        CustomUserModel,
        on_delete=models.CASCADE
    )
    data_id = models.AutoField(primary_key=True)
    dictdata = models.JSONField()
    datasave = models.CharField(max_length=256)
    is_delete = models.BooleanField(default=False)
    class Meta:
        verbose_name = "DataOperationModel"
