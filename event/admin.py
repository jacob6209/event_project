from django.contrib import admin
from .models import (
    EventType, Event, Course,
    Priority, Participant,
    Registration, FoodReservation,RegisteredParticipant,Guest
)

@admin.register(RegisteredParticipant)
class ReegistrayionParticipant(admin.ModelAdmin):
    list_display = ('get_user','get_registration_id','participant', 'get_course_event', 'registered_at', 'is_reserved')
    list_filter = ('is_reserved', 'registered_at')
    search_fields = ('participant__full_name', 'registration__course__title','registration__user')
    readonly_fields = ('registered_at',)

    def get_registration_id(self,obj):
        return obj.registration.transaction_id
    get_registration_id.short_description = 'transaction'

    def get_course_event(self, obj):
        course_title = obj.registration.course.title
        event_title = obj.registration.course.event.title if obj.registration.course.event else ''
        return f"{event_title} ({course_title})"
    get_course_event.short_description = 'Event (Course)'

    def get_user(self, obj):
        return obj.participant.user.username if obj.participant.user else "-"
    get_user.short_description = 'User'

# EventType Admin
@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

# Guest Admin
@admin.register(Guest)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id","full_name","national_id","registration",)


# Event Admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "event_type", "is_multi_course", "has_food", "allows_guests", "requires_approval")
    list_filter = ("event_type", "has_food", "allows_guests", "requires_approval")
    search_fields = ("title", "event_type__name")



# Inline Courses inside Event
class CourseInline(admin.TabularInline):
    model = Course
    extra = 1



# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "event", "start_date", "end_date", "capacity")
    list_filter = ("event", "start_date")
    search_fields = ("title", "event__title")
    date_hierarchy = "start_date"


# Priority Admin
@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "level")
    list_filter = ("level",)
    search_fields = ("title",)
    ordering = ("level",)


# Inline FoodReservations inside Registration
class FoodReservationInline(admin.TabularInline):
    model = FoodReservation
    extra = 1

# Participant Admin
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("id","user","user_full_name","full_name","national_id", "relation","is_active" )
    list_editable=("is_active",)
    search_fields = ("full_name", "national_id")
    inlines = [FoodReservationInline]

    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description="User Full Nam"


# Registration Admin
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("id","transaction_id","user", "course", "status", "registered_at")
    list_filter = ("status", "course")
    search_fields = ("participant__full_name", "course__title")
    



# FoodReservation Admin
@admin.register(FoodReservation)
class FoodReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "participant", "meal_type", "count")
    list_filter = ("meal_type",)