from django import forms

from event.utils import persian_to_english_numbers
from .models import Participant,Guest,Registration,RegisteredParticipant

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
        national_id = persian_to_english_numbers(national_id)
        print(national_id)
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
        # جلوگیری از کرش برنامه اگر رجیستریشن خالی باشد
        if not registration:
            return cleaned_data        
        event = registration.event

         # --- TOTAL GUEST CAPACITY ---
        current_guests_count = Guest.objects.filter(registration=registration,status="accepted").count()
        if registration.event.max_guests is not None and current_guests_count >= registration.event.max_guests:
            raise forms.ValidationError(
                "ظرفیت پذیرش مهمان تکمیل شده است"
            )
        # --- PER USER GUEST LIMIT ---
        user_guest_count = Guest.objects.filter(
            registration__user=self.user,
            registration__course__event=registration.event
            # registration=registration,
        ).count()
        print(f'user_guest_count====>{user_guest_count}')

        if user_guest_count >= event.max_guests_per_user:
            raise forms.ValidationError(
                "سقف درخواست شما برای ثبت مهمان در این رویداد تکمیل شده است"
            )
        # --- DUPLICATE NATIONAL ID ---
        if national_id and registration:
            # Check in Guest model
            if Guest.objects.filter(national_id=national_id, registration=registration).exists():
                raise forms.ValidationError(
                    "این کد ملی قبلاً برای این رویداد ثبت شده است."
                )
               # Check in RegistrationParticipant / Participant model
            if RegisteredParticipant.objects.filter(
                registration=registration,
                participant__national_id=national_id
            ).exists():
                raise forms.ValidationError(
                    "این کد ملی قبلاً به عنوان شرکت‌کننده برای این رویداد ثبت شده است."
                )
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user #Save the user 

        if user:
            self.fields['registration'].queryset = (
                Registration.objects.filter(user=user,status='pending')
            )
        