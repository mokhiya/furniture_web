from os import path

from django.contrib.auth import views

app_name = 'common'

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
]