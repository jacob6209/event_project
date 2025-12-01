from django.urls import path
from .views import registration_view,full_registration_view
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', full_registration_view, name='registration'),
    path('index/', TemplateView.as_view(template_name="index.html"),name="index"),
]