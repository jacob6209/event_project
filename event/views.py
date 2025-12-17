from django.shortcuts import render, get_object_or_404
from .models import Participant, RegisteredParticipant, Registration, Course
from django.contrib.auth.decorators import login_required
from .forms import ParticipantActiveForm
from django.contrib import messages
from django.db import transaction

@login_required
def reregistration_view(request):
    user = request.user
    participants = Participant.objects.filter(user=user).filter(is_active=True)
    courses = Course.objects.all()

    # Create forms for each participant
    participant_forms = [
        (p, ParticipantActiveForm(prefix=str(p.id), instance=p))
        for p in participants
    ]

    if request.method == 'POST':
        selected_course_id = request.POST.get('course')
        if not selected_course_id:
            # If no course selected, reload page with error
            return render(request, 'reregistration.html', {
                'participant_forms': participant_forms,
                'courses': courses,
                'error': 'لطفا یک دوره انتخاب کنید.'
            })

        # Safely get course
        selected_course = get_object_or_404(Course, id=selected_course_id)
        selected_event_type = selected_course.event.event_type

        # check if the user already registered for this EVENT TYPE
        already_registered = Registration.objects.filter(
            user=user,
            course__event__event_type=selected_event_type
        ).exists()

        if already_registered:
            messages.error(
                request,
                "شما قبلاً در این رویداد ثبت‌ نام کرده‌اید. امکان ثبت‌ نام دوباره وجود ندارد."
            )
                # Rebuild forms and stop execution
            participant_forms = [
                (p, ParticipantActiveForm(prefix=str(p.id), instance=p))
                for p in participants
            ]
            return render(request, 'reregistration.html', {
                'participant_forms': participant_forms,
                'courses': courses,
            })
        
        with transaction.atomic():
            # Get or create registration for this user and course
            # registration, created = Registration.objects.get_or_create(
            #     user=user,
            #     course=selected_course
            # )
            # Only "Create" Caz already had check before and sure it not Exist
            registration = Registration.objects.create(
                user=user,
                course=selected_course
            )
            # Process each participant form
            for p, form in participant_forms:
                form = ParticipantActiveForm(request.POST, prefix=str(p.id), instance=p)
                if form.is_valid():
                    is_reserved = form.cleaned_data['is_reserved']

                    RegisteredParticipant.objects.update_or_create(
                        registration=registration,
                        participant=p,
                        defaults={'is_reserved': is_reserved}
                    )

        transaction_code= registration.id

        return render(request,'success.html',{"transaction_code":transaction_code})  # replace with your actual success URL

    return render(request,
        'reregistration.html', {
        'participant_forms': participant_forms,
        'courses': courses,
    })
