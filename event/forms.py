from django import forms
from .models import Participant,Guest,Registration

class ParticipantActiveForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['is_reserved']
        widgets = {
            'is_reserved': forms.CheckboxInput(attrs={'class': 'participant-checkbox'})
        }

class GuestForm(forms.ModelForm):
    registration = forms.ModelChoiceField(
        queryset=Registration.objects.none(),
        label="دوره ثبت‌نام‌شده",
        empty_label="انتخاب دوره",
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={
        'required': '* انتخاب دوره الزامی است',
        'invalid_choice': 'دوره انتخاب‌شده معتبر نیست.',
        }
    )

    class Meta:
        model = Guest
        fields = ['registration','full_name', 'national_id', 'relation']
        
    
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
                'required': '* لطفا نام و نام خانوادگی را وارد کنید.',
            },
            'national_id': {
                'required': '* لطفا کد ملی را وارد کنید.',
                'max_length': '* کد ملی نمی‌تواند بیش از ۱۰ رقم باشد.',
                'min_length': '* کد ملی باید ۱۰ رقم باشد.'
            },
            'relation': {
                'required': '* لطفا نسبت را وارد کنید.',
            }
        }
        
            # Custom validation for national_id
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id:  # empty field
            raise forms.ValidationError("* لطفا کد ملی  را وارد کنید.")
        if not national_id.isdigit():
            raise forms.ValidationError("* کد ملی باید فقط شامل اعداد باشد.")
        if len(national_id) != 10:
            raise forms.ValidationError("* کد ملی باید دقیقا ۱۰ رقم باشد.")
        return national_id
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            cleaned_data = {}
        
        national_id = cleaned_data.get('national_id')
        registration = cleaned_data.get('registration')

        # Check if registration allows guests
        if registration:
            if not registration.event.allows_guests:
                raise forms.ValidationError("متاسفانه ثبت مهمان برای این دوره غیر فعال است.")

        # Check if max number of guests is reached
        current_guests_count = Guest.objects.filter(registration=registration).count()
        if registration.event.max_guests is not None and current_guests_count >= registration.event.max_guests:
            raise forms.ValidationError(
                "تعداد مهمانان این دوره به حداکثر رسیده است."
            )

        if national_id and registration:
            # Check if the combination already exists
            if Guest.objects.filter(national_id=national_id, registration=registration).exists():
                raise forms.ValidationError(
                    "این کد ملی قبلاً برای این رویداد ثبت شده است."
                )
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['registration'].queryset = (
                Registration.objects.filter(user=user,status='pending')
            )
        