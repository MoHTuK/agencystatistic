from django.contrib.auth.models import User
from django.db import models


class LadyPhoto(models.Model):
    Img_url = models.CharField(max_length=255)
    Lady_ID = models.ForeignKey(User, on_delete=models.CASCADE)


class ManAcc(models.Model):
    Id = models.CharField(max_length=255)
    Last_msg = models.TextField(default='Nothing')
    Last_msg_date = models.DateField(auto_now=True)


