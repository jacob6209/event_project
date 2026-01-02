from django.urls import path

from config import settings
from .views import reregistration_view\
                    ,registration_lookup_view,my_events_view\
                    ,registration_edit_view,registration_delete_view\
                    ,register_guest,delete_guest,staff_events\
                    ,staff_add_event,event_type_step,event_step\
                    ,course_step,confirm_step,index,event_detail,request_review_list\
                    ,request_review_action
from django.views.generic import TemplateView
from django.conf.urls.static import static
urlpatterns = [
    path('register/', reregistration_view, name='reregistration'),
    path('index/', index, name='index'),
    # path('index/', TemplateView.as_view(template_name="index.html"),name="index"),
    path("my_events/",my_events_view, name="my_events"),
    path("registration/guest/",register_guest, name="registration_guest"),
    # delete an Guest
    path("guest/delete/<int:guest_id>/", delete_guest, name="delete_guest"),
    # delete whole registration
    path("registration/delete/<int:registration_id>/",registration_delete_view,name="registration_delete"),
    path("registration/lookup/<str:code>/", registration_lookup_view, name="registration_lookup"),
    path("registration/edit/<int:registration_id>/",registration_edit_view,name="registration_edit"),
    # stuff path
    path("staff_events/",staff_events,name="staff_events"),
    path("staff_add_event/",staff_add_event,name="staff_add_event"),
    path("wizard/event-type/", event_type_step, name="wizard_event_type"),
    path("wizard/event/", event_step, name="wizard_event"),
    path("wizard/course/",course_step , name="wizard_course"),
    path("wizard/confirm/",confirm_step , name="wizard_confirm"),
    path("request_review/",request_review_list , name="request_review"),
    path("request_review/",request_review_list , name="request_review_list"),
    path("request_review/<int:registration_id>/action/",
        request_review_action,
        name="request_review_action"
    ),

    path("wizard/detail/",event_detail , name="event_detail"),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )