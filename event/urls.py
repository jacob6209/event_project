from django.urls import path
from .views import reregistration_view,registration_lookup_view,my_events_view,registration_edit_view,registration_delete_view
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', reregistration_view, name='reregistration'),
    path('index/', TemplateView.as_view(template_name="index.html"),name="index"),
    path("my_events/",my_events_view, name="my_events"),
    path("registration/delete/<int:registration_id>/",registration_delete_view,name="registration_delete"),
    # path("registration/lookup/", registration_lookup_form, name="registration_lookup_form"),
    path("registration/lookup/<str:code>/", registration_lookup_view, name="registration_lookup"),
    path("registration/edit/<int:registration_id>/",registration_edit_view,name="registration_edit"),
]