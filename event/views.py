from django.shortcuts import render, redirect
from django.forms import inlineformset_factory,formset_factory
from .models import Registration, Participant
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import ParticipantFormSet, RegistrationForm, FoodReservationFormSet,ParticipantForm,ParticipantActiveForm


@login_required
def reregistration_view(request):
    user = request.user
    participants = Participant.objects.filter(user=user)

    # Combine each participant with its form
    participant_forms = [
        (p, ParticipantActiveForm(prefix=str(p.id), instance=p)) for p in participants
    ]

    if request.method == 'POST':
        for p, form in participant_forms:
            form = ParticipantActiveForm(request.POST, prefix=str(p.id), instance=p)
            if form.is_valid():
                form.save()
        return redirect('success_page')  # replace with your success URL

    return render(request, 'reregistration.html', {
        'participant_forms': participant_forms
    })