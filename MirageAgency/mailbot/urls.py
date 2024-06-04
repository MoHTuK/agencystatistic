from django.urls import path


from mailbot.views import *

urlpatterns = [
    path('mailbot', mailbot, name='mailbot'),
    # path('proxy/onlineman', proxy_online_man, name='proxy_onlineman'),
    path('proxy/send_msg', proxy_send_msg, name='proxy_send'),
    path('proxy/save_to_blacklist', add_in_blacklist, name='add_blacklist'),
    path('proxy/save_to_goldman', add_in_goldman, name='add_goldman'),
    path('proxy/status', proxy_status, name='proxy_status')
]