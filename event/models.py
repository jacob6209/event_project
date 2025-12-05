from django.db import models
from django.contrib.auth import get_user_model

class EventType(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=300)
    is_multi_course = models.BooleanField(default=False)
    rules = models.TextField(blank=True)
    has_food = models.BooleanField(default=False)
    allows_guests = models.BooleanField(default=False)     
    requires_approval = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.event_type})"


class Course(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    capacity = models.PositiveIntegerField()
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()

    def __str__(self):
        return f"{self.event.title} - {self.title}"


class Priority(models.Model):
    title = models.CharField(max_length=100)
    level = models.IntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['level']

    def __str__(self):
        return self.title


class Participant(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="participants"
    )
    full_name = models.CharField(max_length=200)
    national_id = models.CharField(max_length=20)
    relation = models.CharField(
        max_length=20,
        choices=[
            ('self', 'خودم'),
            ('spouse', 'همسر'),
            ('child', 'فرزند'),
            ('guest', 'مهمان')
        ]
    )

    # Add new BooleanField
    is_active = models.BooleanField(default=True)
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    

        
User = get_user_model()
class Registration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    priority = models.ForeignKey(Priority,on_delete=models.SET_NULL,null=True,blank=True)
          
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],  # restricts user to same course only once
                name='unique_user_course'
            ),
        ]

    @property
    def event(self):
        return self.course.event

    def __str__(self):
        return f"{self.course}"
    
    
    


class FoodReservation(models.Model):
    MEAL_TYPE_CHOICES = [
        ('all', 'همه وعده ها'),
        ('breakfast', 'صبحانه'),
        ('lunch', 'ناهار'),
        ('dinner', 'شام'),
    ]
    meal_type = models.CharField(max_length=20,default=MEAL_TYPE_CHOICES[0][0], choices=MEAL_TYPE_CHOICES)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="food_reservations")
    count = models.PositiveIntegerField(default=1)


class RegisteredParticipant(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"Registered: {self.participant.full_name} for {self.registration.course.title}"
    

    class Meta:
        unique_together = ('participant', 'registration')

# #  اولویت بندیها 
# class PriorityCriterion(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)  
#     weight = models.IntegerField(default=1)  

#     def __str__(self):
#         return self.title

# # 
# class EventPrioritySetting(models.Model):
#     event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
#     criterion = models.ForeignKey(PriorityCriterion, on_delete=models.CASCADE)
#     is_enabled = models.BooleanField(default=True)
#     weight_override = models.IntegerField(null=True, blank=True)

#     def get_effective_weight(self):
#         return self.weight_override if self.weight_override is not None else self.criterion.weight
