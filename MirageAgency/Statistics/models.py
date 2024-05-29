from django.contrib.auth.models import User
from django.db import models


class Transaction(models.Model):
    Lady_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    Man_ID = models.IntegerField()
    Sum = models.FloatField()
    Operation_type = models.CharField(max_length=255)
    Date = models.CharField(max_length=255)