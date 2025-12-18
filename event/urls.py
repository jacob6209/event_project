from django.urls import path
from .views import reregistration_view,registration_lookup_view
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', reregistration_view, name='registration'),
    path('index/', TemplateView.as_view(template_name="index.html"),name="index"),
    # path("registration/lookup/", registration_lookup_form, name="registration_lookup_form"),
    path("registration/lookup/<str:code>/", registration_lookup_view, name="registration_lookup"),
]