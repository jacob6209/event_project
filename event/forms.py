

from django import forms
from django.forms import inlineformset_factory, formset_factory,modelformset_factory
from .models import Participant, Registration, FoodReservation

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['full_name', 'national_id', 'relation', 'priority']

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['course',]
       

class FoodReservationForm(forms.ModelForm):
    class Meta:
        model = FoodReservation
        fields = ['meal_type', 'count']

ParticipantFormSet = modelformset_factory(
    Participant,
    form=ParticipantForm,
    extra=1,
    can_delete=True
)

# ParticipantFormSet = formset_factory(ParticipantForm, extra=1, can_delete=True)

FoodReservationFormSet = inlineformset_factory(
    Registration,
    FoodReservation,
    form=FoodReservationForm,
    extra=1,
    can_delete=True
)