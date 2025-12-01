from django.urls import path
from .views import registration_view

urlpatterns = [
    path('register/setp1/', registration_view, name='participant_step'),
]