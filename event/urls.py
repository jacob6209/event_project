from django.urls import path
from .views import reregistration_view
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', reregistration_view, name='registration'),
    # path('register/<int:course_id>/', reregistration_view, name='reregistration'),
    path('index/', TemplateView.as_view(template_name="index.html"),name="index"),
]