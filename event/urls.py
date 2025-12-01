from django.urls import path
from .views import registration_view,full_registration_view

urlpatterns = [
    path('register/', full_registration_view, name='registration'),
]