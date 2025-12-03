from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from .models import Registration, Participant

from .forms import ParticipantFormSet, RegistrationForm, FoodReservationFormSet

def full_registration_view(request):
    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST)
        participant_formset = ParticipantFormSet(request.POST)
        participant_food_pairs = []

        if registration_form.is_valid() and participant_formset.is_valid():
            registration = registration_form.save(commit=False)
            participants = participant_formset.save(commit=False)
            valid = True

            # Create a food formset for each participant
            for i, participant_form in enumerate(participant_formset.forms):
                prefix = f'food-{i}'
                food_formset = FoodReservationFormSet(
                    request.POST, instance=participants[i], prefix=prefix
                )
                participant_food_pairs.append((participant_form, food_formset))
                if not food_formset.is_valid():
                    valid = False

            if valid:
                registration.save()  # save registration if needed

                for participant, food_formset in zip(participants, [f[1] for f in participant_food_pairs]):
                    participant.save()  # save participant first
                    food_formset.instance = participant  # link food to participant
                    food_formset.save()

                return redirect('success')

    else:
        registration_form = RegistrationForm()
        participant_formset = ParticipantFormSet(queryset=Participant.objects.none())
        participant_food_pairs = []

        for i, participant_form in enumerate(participant_formset.forms):
            prefix = f'food-{i}'
            food_formset = FoodReservationFormSet(prefix=prefix)
            participant_food_pairs.append((participant_form, food_formset))

    return render(request, 'full_registration.html', {
        'registration_form': registration_form,
        'participant_formset': participant_formset,
        'participant_food_pairs': participant_food_pairs,
    })



# js solution
# def registration_view(request):
#     if request.method == "POST":
#         reg_form = RegistrationForm(request.POST)
#         participant_forms_data = request.POST.getlist('participant_data')  # JSON string for each participant
        
#         if reg_form.is_valid():
#             course = reg_form.cleaned_data['course']

#             import json
#             for pdata_json in participant_forms_data:
#                 pdata = json.loads(pdata_json)
#                 participant = Participant.objects.create(
#                     full_name=pdata['full_name'],
#                     national_id=pdata['national_id'],
#                     relation=pdata['relation'],
#                     priority_id=pdata['priority'] if pdata['priority'] else None
#                 )
#                 Registration.objects.create(course=course, participant=participant)

#             return redirect('success')

#     else:
#         reg_form = RegistrationForm()

#     participant_form = ParticipantForm()
#     return render(request, 'registration_form.html', {
#         'reg_form': reg_form,
#         'participant_form': participant_form
#     })

# solution 1
# Create an inline formset
# ParticipantFormSet = inlineformset_factory(
#     Registration, Participant, form=ParticipantForm, extra=1, can_delete=True
# )
# def registration_form(request):
#     if request.method == "POST":
#         reg_form = RegistrationForm(request.POST)
#         formset = ParticipantFormSet(request.POST)
        
#         if reg_form.is_valid():
#             registration = reg_form.save()
#             # Bind formset to the saved registration
#             formset = ParticipantFormSet(request.POST, instance=registration)
            
#             if formset.is_valid():
#                 formset.save()
#                 return redirect("success")
#     else:
#         reg_form = RegistrationForm()
#         formset = ParticipantFormSet()

#     return render(request, "registration_form.html", {
#         "reg_form": reg_form,
#         "formset": formset,
#     })


#  solution 2
# def participant_view(request):
#     if request.method == 'POST':
#         form = ParticipantForm(request.POST)
#         if form.is_valid():
#             request.session['participant_data'] = form.cleaned_data
#             return redirect('registration_step')
#     else:
#         form = ParticipantForm()
    
#     return render(request, 'participant_form.html', {'form': form})

# def registration_view(request):
#     participant_data = request.session.get('participant_data', None)
#     if not participant_data:
#         return redirect('participant_step')  # Redirect if no participant data exists

#     # Now handle the registration form
#     if request.method == 'POST':
#         # Process the registration form and store the full data
#         # Save to DB or process
#         return redirect('success_page')

#     return render(request, 'registration_form.html', {'participant_data': participant_data})