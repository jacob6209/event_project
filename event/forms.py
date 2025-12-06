from django import forms
from .models import Participant

class ParticipantActiveForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['is_reserved']
        widgets = {
            'is_reserved': forms.CheckboxInput(attrs={'class': 'participant-checkbox'})
        }

