from django import forms
from .models import Participant

class ParticipantActiveForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'participant-checkbox'})
        }

# class ParticipantForm(forms.ModelForm):
#     class Meta:
#         model = Participant
#         fields = ['full_name', 'national_id', 'relation', 'is_active']

#         labels = {
#             'full_name': 'نام ',
#             'national_id': 'کد ملی',
#             'relation': 'رابطه',
#             'is_active':'رزرو'
#         }

#         help_texts = {
#             'full_name': 'لطفاً نام کامل خود را وارد کنید.',
#             'national_id': 'کد ملی خود را وارد کنید.',
#             'relation': 'رابطه شما با شخص ثبت‌نام‌شده را وارد کنید.',
#             'is_active': 'رزرو و عدم رزرو کاربر را وارد کنید.',
#         }

#         widgets = {
#             'full_name': forms.TextInput(attrs={'placeholder': 'نام کامل'}),
#             'national_id': forms.TextInput(attrs={'placeholder': 'کد ملی'}),
#         }

# ParticipantFormSet = modelformset_factory(
#     Participant,
#     fields=['full_name', 'national_id', 'relation','is_active'],
#     extra=1  # How many empty participant forms to show
# )


# class RegistrationForm(forms.ModelForm):
#     class Meta:
#         model = Registration
#         fields = ['course']

#         labels = {
#             'course': 'دوره',
#         }
#         help_texts = {
#             'course': 'دوره‌ای که می‌خواهید در آن ثبت‌نام کنید را انتخاب کنید.',
#         }

#         widgets = {
#             'course': forms.Select(attrs={'placeholder': 'انتخاب دوره'}),
#         }


# class FoodReservationForm(forms.ModelForm):
#     class Meta:
#         model = FoodReservation
#         fields = ['meal_type', 'count']

#         labels = {
#             'meal_type': 'نوع وعده غذایی',
#             'count': 'تعداد',
#         }

#         help_texts = {
#             'meal_type': 'نوع وعده غذایی خود را انتخاب کنید.',
#             'count': 'تعداد وعده‌های غذایی مورد نیاز را وارد کنید.',
#         }

#         widgets = {
#             'meal_type': forms.Select(attrs={'placeholder': 'انتخاب وعده غذایی'}),
#             'count': forms.NumberInput(attrs={'placeholder': 'تعداد'}),
#         }

    



# FoodReservationFormSet = inlineformset_factory(
#     Participant,
#     FoodReservation,
#     form=FoodReservationForm,
#     extra=1,
#     can_delete=True
# )
