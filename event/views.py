from django.shortcuts import render, redirect
from .models import Participant,RegisteredParticipant,Registration,Course
from django.contrib.auth.decorators import login_required

from .forms import ParticipantActiveForm


@login_required
def reregistration_view(request):
    user = request.user
    participants = Participant.objects.filter(user=user)
    courses = Course.objects.all()  # Get all available courses

    # Combine each participant with its form
    participant_forms = [
        (p, ParticipantActiveForm(prefix=str(p.id), instance=p)) for p in participants
    ]

    if request.method == 'POST':
        # Create or get Registration for this user
        registration, created = Registration.objects.get_or_create(user=user)

        # Get the selected course
        selected_course_id = request.POST.get('course')
        selected_course = Course.objects.get(id=selected_course_id) if selected_course_id else None

        for p, form in participant_forms:
            form = ParticipantActiveForm(request.POST, prefix=str(p.id), instance=p)
            if form.is_valid():
                # Save into RegisteredParticipant
                is_active = form.cleaned_data['is_active']
                RegisteredParticipant.objects.update_or_create(
                    participant=p,
                    registration=registration,
                    course=selected_course,
                    defaults={'is_active': is_active}  # Explicitly map field
                )
        
        # You can update any Registration fields here if needed
        # For example: registration.last_updated = timezone.now()
        # registration.save()

        return redirect('success_page')

    return render(request, 'reregistration.html', {
        'participant_forms': participant_forms,
        'courses': courses,
    })
