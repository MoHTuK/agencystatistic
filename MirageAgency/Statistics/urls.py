from django.urls import path


from Statistics.views import *

urlpatterns = [
    path('', statistics, name='statistics'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('acc_info', get_acc_info, name='acc_info')

]
