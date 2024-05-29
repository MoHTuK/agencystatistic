from django.urls import path


from mailbot.views import *

urlpatterns = [
    path('mailbot', mailbot, name='mailbot')
]