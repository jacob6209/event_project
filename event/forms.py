from django import forms
from .models import Participant,Guest

class ParticipantActiveForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['is_reserved']
        widgets = {
            'is_reserved': forms.CheckboxInput(attrs={'class': 'participant-checkbox'})
        }

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['full_name', 'national_id', 'relation']
        
        # Custom widgets for nicer UI
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'title': 'نام و نام خانوادگی مهمان را وارد کنید'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control', 
                'title': 'کد ملی ۱۰ رقمی مهمان را وارد کنید'
            }),
            'relation': forms.TextInput(attrs={
                'class': 'form-control', 
                'title': 'نسبت مهمان با شما را وارد کنید',
                'required': 'required',
            }),
        }

        # Optional: custom labels
        labels = {
            'full_name': 'نام و نام خانوادگی',
            'national_id': 'کد ملی',
            'relation': 'نسبت با شما',
        }


        # Optional: custom error messages
        error_messages = {
            'full_name': {
                'required': '* لطفا نام کامل مهمان را وارد کنید.',
            },
            'national_id': {
                'required': '* لطفا کد ملی مهمان را وارد کنید.',
                'max_length': '* کد ملی نمی‌تواند بیش از ۱۰ رقم باشد.',
                'min_length': '* کد ملی باید ۱۰ رقم باشد.'
            },
            'relation': {
                'required': '* لطفا نسبت مهمان را وارد کنید.',
            }
        }
            # Custom validation for national_id
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id:  # empty field
            raise forms.ValidationError("* لطفا کد ملی مهمان را وارد کنید.")
        if not national_id.isdigit():
            raise forms.ValidationError("* کد ملی باید فقط شامل اعداد باشد.")
        if len(national_id) != 10:
            raise forms.ValidationError("* کد ملی باید دقیقا ۱۰ رقم باشد.")
        return national_id