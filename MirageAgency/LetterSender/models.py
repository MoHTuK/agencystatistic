from django.contrib.auth.models import User
from django.db import models


class LadyPhoto(models.Model):
    Img_url = models.CharField(max_length=255)
    Lady_ID = models.ForeignKey(User, on_delete=models.CASCADE)


class ManAcc(models.Model):
    Id = models.CharField(max_length=255)
    Message_status = models.BooleanField(default=False)

