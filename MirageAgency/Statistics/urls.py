from django.urls import path


from Statistics.views import *

urlpatterns = [
    path('', statistics, name='statistics'),
    path('login/', login_view, name='login'),

]
