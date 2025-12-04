from django.contrib import admin
from .models import (
    EventType, Event, Course,
    Priority, Participant,
    Registration, FoodReservation
)



# EventType Admin
@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


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
    list_display = ("id", "full_name","is_active","national_id", "relation", "user")
    search_fields = ("full_name", "national_id")
    inlines = [FoodReservationInline]




# Registration Admin
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "status", "registered_at")
    list_filter = ("status", "course")
    search_fields = ("participant__full_name", "course__title")
    



# FoodReservation Admin
@admin.register(FoodReservation)
class FoodReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "participant", "meal_type", "count")
    list_filter = ("meal_type",)