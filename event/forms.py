from django import forms
from allauth.account.forms import LoginForm
from django.forms import inlineformset_factory, modelformset_factory
from .models import Participant, Registration, FoodReservation


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['full_name', 'national_id', 'relation', 'priority']

        labels = {
            'full_name': 'نام ',
            'national_id': 'کد ملی',
            'relation': 'رابطه',
            'priority': 'اولویت',
        }

        help_texts = {
            'full_name': 'لطفاً نام کامل خود را وارد کنید.',
            'national_id': 'کد ملی خود را وارد کنید.',
            'relation': 'رابطه شما با شخص ثبت‌نام‌شده را وارد کنید.',
            'priority': 'اولویت خود را مشخص کنید.',
        }

        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'نام کامل'}),
            'national_id': forms.TextInput(attrs={'placeholder': 'کد ملی'}),
            'priority': forms.Select(attrs={'placeholder': 'اولویت'}),
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['course']

        labels = {
            'course': 'دوره',
        }
        help_texts = {
            'course': 'دوره‌ای که می‌خواهید در آن ثبت‌نام کنید را انتخاب کنید.',
        }

        widgets = {
            'course': forms.Select(attrs={'placeholder': 'انتخاب دوره'}),
        }


class FoodReservationForm(forms.ModelForm):
    class Meta:
        model = FoodReservation
        fields = ['meal_type', 'count']

        labels = {
            'meal_type': 'نوع وعده غذایی',
            'count': 'تعداد',
        }

        help_texts = {
            'meal_type': 'نوع وعده غذایی خود را انتخاب کنید.',
            'count': 'تعداد وعده‌های غذایی مورد نیاز را وارد کنید.',
        }

        widgets = {
            'meal_type': forms.Select(attrs={'placeholder': 'انتخاب وعده غذایی'}),
            'count': forms.NumberInput(attrs={'placeholder': 'تعداد'}),
        }


# Create formset for Participants
ParticipantFormSet = modelformset_factory(
    Participant,
    form=ParticipantForm,
    extra=1,
    can_delete=True
)

# Create inline formset for FoodReservations
FoodReservationFormSet = inlineformset_factory(
    Registration,
    FoodReservation,
    form=FoodReservationForm,
    extra=1,
    can_delete=True
)
