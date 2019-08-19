from django.urls import path
from .views import *
urlpatterns = [
    path('messenger', MessengerApiView.as_view(), name='messenger_api_view'),
]
