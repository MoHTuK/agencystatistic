from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Blacklist)
class Blacklist_Admin(admin.ModelAdmin):
    list_display = ['lady_id', 'man_id']


@admin.register(GoldMan)
class Blacklist_Admin(admin.ModelAdmin):
    list_display = ['man_id']
