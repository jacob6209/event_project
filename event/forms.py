from event.utils import english_to_persian_numbers, persian_to_english_numbers
from .models import Participant,Guest,Registration,RegisteredParticipant,Event,EventType,Course

from django import forms
from .models import Event, EventType
from django.forms import inlineformset_factory, modelformset_factory

from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

class FilterForm(forms.Form):

    start_date = JalaliDateField(
        required=False,
        label="تاریخ شروع",
        widget=AdminJalaliDateWidget(attrs={"class": "form-section__input"})
    )

    end_date = JalaliDateField(
        required=False,
        label="تاریخ پایان",
        widget=AdminJalaliDateWidget(attrs={"class": "form-section__input"})
    )

class CourseDateForm(forms.ModelForm):

    title = forms.CharField(
    label="عنوان دوره",
    required=True,
    error_messages={
            "required": "این فیلد اجباری است"
        },
    widget=forms.TextInput(attrs={
        "placeholder": "مثلاً: دوره اول:از تاریخ ۲۷ اسفند تا ۳ فروردین"
    })
    )

    start_date = JalaliDateField(
        required=True,
        label="تاریخ شروع",
        error_messages={
            "required": "این فیلد اجباری است"
        },
        widget=AdminJalaliDateWidget(attrs={"class": "form-section__input"})
    )

    end_date = JalaliDateField(
        required=True,
        label="تاریخ پایان",
        error_messages={
            "required": "این فیلد اجباری است"
        },
        widget=AdminJalaliDateWidget(attrs={"class": "form-section__input"})
    )

    registration_start = JalaliDateField(
        required=True,
        label="شروع ثبت نام",
        error_messages={
            "required": "این فیلد اجباری است"
        },
        widget=AdminJalaliDateWidget(attrs={"class": "form-section__input"})
    )

    registration_end = JalaliDateField(
        required=True,
        label="پایان ثبت نام",
        error_messages={
            "required": "این فیلد اجباری است"
        },
        widget=AdminJalaliDateWidget(attrs={"class": "form-section__input"})
    )

    max_capacity = forms.IntegerField(
        required=True,
        label="حداکثر ظرفیت",
        min_value=1,
        initial=10
    )

    max_guests = forms.IntegerField(
        required=True,
        label="ظرفیت مهمان",
        min_value=0,
        initial=0
    )

    max_guests_per_user = forms.IntegerField(
        required=True,
        label="حداکثر مهمان برای هر کاربر",
        min_value=0,
        initial=0
    )

    has_food = forms.BooleanField(
        label="وعده غذایی",
        required=False
    )

    allows_guests = forms.BooleanField(
        label="پذیرش میهمان",
        required=False
    )

    requires_approval = forms.BooleanField(
        label="نیاز به تأیید",
        required=False
    )
    class Meta:
        model = Course
        fields = [
            'title',
            'start_date',
            'end_date',
            'registration_start',
            'registration_end',
            'max_capacity',
            'max_guests',
            'max_guests_per_user',
            'has_food',
            'allows_guests',
            'requires_approval',
        ]
        def clean(self):
            cleaned_data = super().clean()
            # Check if any field is empty
            required_fields = [
                "title", "start_date", "end_date",
                "registration_start", "registration_end",
                "max_capacity", "max_guests", "max_guests_per_user"
            ]
            for field in required_fields:
                if cleaned_data.get(field) in [None, ""]:
                    self.add_error(field, "این فیلد الزامی است")
            return cleaned_data



CourseDateFormSet = modelformset_factory(
    Course,
    form=CourseDateForm,
    extra=1,
    can_delete=False
)

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ["name", "description"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "event_type",
            "title",
            "image",
            "is_multi_course",
            "rules",
            "has_food",
            "allows_guests",
            "max_guests",
            "requires_approval",
            "max_capacity",
            "max_guests_per_user",
        ]

        widgets = {
            "event_type": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "rules": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "max_guests": forms.NumberInput(attrs={"class": "form-control"}),
            "max_capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "max_guests_per_user": forms.NumberInput(attrs={"class": "form-control"}),

            "is_multi_course": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "has_food": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "allows_guests": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "requires_approval": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        allows_guests = cleaned_data.get("allows_guests")
        max_guests = cleaned_data.get("max_guests")

        if allows_guests and max_guests == 0:
            self.add_error(
                "max_guests",
                "وقتی مهمان مجاز است، تعداد مهمان باید بیشتر از صفر باشد."
            )

        return cleaned_data
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "event",
            "title",
            "start_date",
            "end_date",
            "registration_start",
            "registration_end",
            "max_capacity",
        ]

        widgets = {
            "event": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),

            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),

            "registration_start": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "registration_end": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),

            "max_capacity": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        reg_start = cleaned_data.get("registration_start")
        reg_end = cleaned_data.get("registration_end")

        if start_date and end_date and start_date > end_date:
            self.add_error(
                "end_date",
                "تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد."
            )

        if reg_start and reg_end and reg_start >= reg_end:
            self.add_error(
                "registration_end",
                "پایان ثبت‌نام باید بعد از شروع ثبت‌نام باشد."
            )

        if start_date and reg_end and reg_end.date() > start_date:
            self.add_error(
                "registration_end",
                "ثبت‌نام باید قبل از شروع دوره به پایان برسد."
            )

        return cleaned_data

# Inline formset for courses
CourseFormSet = inlineformset_factory(
    Event, Course, form=CourseForm, extra=1, can_delete=True
)

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
        widget=forms.Select(attrs={
        'class': 'form-control',
        'required': 'required', 
        }),
        error_messages={
        'required': '* انتخاب دوره الزامی است',
        'invalid_choice': 'دوره انتخاب‌شده معتبر نیست.',
        }
    )

    class Meta:
        model = Guest
        fields = ["registration",'full_name', 'national_id', 'relation']
        
    
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
        if not national_id:  # empty field
            raise forms.ValidationError("* لطفا کد ملی  را وارد کنید.")
        if not national_id.isdigit():
            raise forms.ValidationError("* کد ملی باید فقط شامل اعداد باشد.")
        if len(national_id) != 10:
            raise forms.ValidationError("* کد ملی باید دقیقا ۱۰ رقم باشد.")
        return national_id
    
    
    def clean(self):
        cleaned_data = super().clean()
        registration = cleaned_data.get("registration")

        if not registration:
            raise forms.ValidationError("لطفا یک دوره را انتخاب کنید.")
        
        national_id = cleaned_data.get('national_id')     
        event = registration.course.event

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

class GuestEditForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['full_name', 'national_id', 'relation', 'is_reserved'] 

        widgets = {
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'is_reserved': forms.CheckboxInput(attrs={'class': 'participant-checkbox'}),
          }
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        national_id = persian_to_english_numbers(national_id)
        
        if not national_id:  # empty field
            raise forms.ValidationError("*لطفا کد ملی را وارد کنید.")
        if not national_id.isdigit():
            raise forms.ValidationError("*کد ملی باید عددی باشد.")
        if len(national_id) != 10:
            raise forms.ValidationError("*کد ملی 10 رقمی است.")
        return national_id
    def clean_full_name(self):
        value = self.cleaned_data.get("full_name", "").strip()
        if not value:
            raise forms.ValidationError("* این فیلد نمی‌تواند خالی باشد")
        return value

    def clean_relation(self):
        value = self.cleaned_data.get("relation", "").strip()
        if not value:
            raise forms.ValidationError("* این فیلد نمی‌تواند خالی باشد")
        return value
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data:
            cleaned_data = {}
        
        national_id = cleaned_data.get('national_id')
        registration = self.instance.registration
        if not registration:
            return cleaned_data        
        # --- DUPLICATE NATIONAL ID ---
        if national_id and registration:
            normalized_national_id = persian_to_english_numbers(national_id)
            # Check in Guest model
            if Guest.objects.filter(national_id=normalized_national_id,
                                    registration=registration).exclude(pk=self.instance.pk).exists():
                
                self.add_error('national_id', " * کد ملی تکراری ")
                raise forms.ValidationError(
                    "این کد ملی قبلاً برای این رویداد ثبت شده است."
                )
            # Check in RegistrationParticipant / Participant model
            if RegisteredParticipant.objects.filter(
                 participant__national_id__in=[
                    normalized_national_id,
                    english_to_persian_numbers(normalized_national_id)
        ]
            ).exists():
                self.add_error('national_id', " * کد ملی تکراری ")
                raise forms.ValidationError(
                    "این کد ملی قبلاً به عنوان شرکت‌کننده برای این رویداد ثبت شده است."
                )
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.national_id:
             self.initial['national_id'] = persian_to_english_numbers(self.instance.national_id)