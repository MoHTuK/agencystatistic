from django.urls import path

from LetterSender.views import *

urlpatterns = [
    path('sender', main_sender_view, name='main_sender_view'),
    path('sender/get_imgs', pars_imgs, name='pars_imgs'),
    path('sender/get_man', pars_id, name='pars_id'),
    path('task_status/<task_id>/', task_status, name='task_status'),
]