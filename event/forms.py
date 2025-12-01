
from django import forms
from .models import Participant,Registration


# solution 2
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['course']  # only select course here
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
        }

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['full_name', 'national_id', 'relation', 'priority']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'relation': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }


# selotion 1
# class ParticipantForm(forms.ModelForm):
#     class Meta:
#         model = Participant
#         fields = ['full_name', 'national_id', 'relation']

# class RegistrationForm(forms.ModelForm):
#     class Meta:
#         model = Registration
#         fields = '__all__'