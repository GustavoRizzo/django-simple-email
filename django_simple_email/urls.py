from django.urls import path

from .views import Home

app_name = 'django_simple_email'

urlpatterns = [
    path('', Home.as_view(), name='home'),
]
