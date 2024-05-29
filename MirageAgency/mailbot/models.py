from django.db import models
from django.contrib.auth.models import User


class Blacklist(models.Model):
    lady_id = models.ForeignKey(User, on_delete=models.CASCADE)
    man_id = models.IntegerField()


class GoldMan(models.Model):
    man_id = models.IntegerField()
