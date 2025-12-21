from django.http import Http404
from django.shortcuts import render, get_object_or_404,redirect
from .models import Participant, RegisteredParticipant, Registration, Course
from django.contrib.auth.decorators import login_required
from .forms import ParticipantActiveForm,GuestForm
from django.contrib import messages
from django.db import transaction

@login_required
def register_guest(request):
    """
    View to handle adding a guest.
    - GET: display empty form
    - POST: validate and save guest
    """
    if request.method == 'POST':
        form = GuestForm(request.POST,user=request.user)
        if form.is_valid():
            guest=form.save()
            messages.success(request, "مهمان با موفقیت ثبت شد!")
            return redirect(guest.registration.get_absolute_url())
       

        # Forward ALL form errors to messages
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
    else:
        form = GuestForm(user=request.user)

    context = {
        'form': form
    }
    return render(request, 'registration_guest.html', context)

@login_required
def registration_delete_view(request, registration_id):
    registration = get_object_or_404(
        Registration,
        id=registration_id,
        user=request.user,
        status="pending"
    )

    if request.method == "POST":
        registration.delete()
        messages.success(request, "ثبت‌نام با موفقیت حذف شد")

    return redirect("my_events")

@login_required
def registration_edit_view(request, registration_id):
    user = request.user

    registration = get_object_or_404(
        Registration,
        id=registration_id,
        user=user,
        status="pending"
    )

    participants = Participant.objects.filter(user=user, is_active=True)
    courses = Course.objects.all()

    # Preselect current course
    selected_course = registration.course

    participant_forms = [
        (p,ParticipantActiveForm(prefix=str(p.id),
                instance=p,
                initial={
                    "is_reserved": RegisteredParticipant.objects.filter(
                        registration=registration,
                        participant=p
                    ).values_list("is_reserved", flat=True).first() or False
                }
            )
        )
        for p in participants
    ]

    if request.method == "POST":
        selected_course_id = request.POST.get("course")

        if not selected_course_id:
            return render(request, "reregistration.html", {
                "participant_forms": participant_forms,
                "courses": courses,
                "selected_course": selected_course,
                "error": "لطفا یک دوره انتخاب کنید."
            })

        selected_course = get_object_or_404(Course, id=selected_course_id)
        selected_event_type = selected_course.event.event_type

        # 🔹 Prevent duplicate registration for the same event type (exclude current registration)
        already_registered = Registration.objects.filter(
            user=user,
            course__event__event_type=selected_event_type
        ).exclude(id=registration.id).exists()

        if already_registered:
            messages.error(
                request,
                "⚠️ شما قبلاً در این رویداد ثبت‌نام کرده‌اید. امکان ثبت‌نام مجدد وجود ندارد."
            )
            # Rebuild forms and stop execution
            participant_forms = [
                (p,ParticipantActiveForm(prefix=str(p.id),
                        instance=p,
                        initial={
                            "is_reserved": RegisteredParticipant.objects.filter(
                                registration=registration,
                                participant=p
                            ).values_list("is_reserved", flat=True).first() or False
                        }
                    )
                )
                for p in participants
            ]
            context={
                'participant_forms': participant_forms,
                'courses': courses,
                "registration": registration,
                "is_edit": True,
                "error": "⚠️ شما قبلاً در این رویداد ثبت‌نام کرده‌اید. امکان ثبت‌نام دوباره وجود ندارد.",
                'selected_course': selected_course,
            }
            return render(request, 'reregistration.html',context)

        with transaction.atomic():
            # ✅ Update registration instead of creating
            registration.course = selected_course
            registration.save(update_fields=["course"])

            for p, _ in participant_forms:
                form = ParticipantActiveForm(
                    request.POST,
                    prefix=str(p.id),
                    instance=p
                )

                if form.is_valid():
                    is_reserved = form.cleaned_data["is_reserved"]

                    RegisteredParticipant.objects.update_or_create(
                        registration=registration,
                        participant=p,
                        defaults={"is_reserved": is_reserved}
                    )

        messages.success(request, "✅ اطلاعات ثبت‌نام با موفقیت ویرایش یافت")
        return redirect(
            "registration_lookup",
            code=registration.transaction_id
        )

    return render(request, "reregistration.html", {
        "participant_forms": participant_forms,
        "courses": courses,
        "selected_course": selected_course,
        "registration": registration,
        "is_edit": True,   # 🔥 useful in template
    })

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
                "شما قبلاً در این رویداد ثبت‌ نام کرده‌اید. امکان ثبت‌ نام مجدد وجود ندارد."
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
                transaction_code= registration.transaction_id
        return redirect("registration_lookup",code=transaction_code)
        # return render(request,'success.html',{"transaction_code":transaction_code})  # replace with your actual success URL

    return render(request,
        'reregistration.html', {
        'participant_forms': participant_forms,
        'courses': courses,
    })

@login_required
def registration_lookup_view(request, code):
    try:
        registration = get_object_or_404(
            Registration,
            transaction_id=code,
            user=request.user
        )
        participants = registration.registeredparticipant_set.select_related("participant")
        course=registration.course
    except Http404:
        return render(
            request,
            "registration_not_found.html",
            status=404
        )
    return render(
        request,
        "registration_lookup.html",
        {
            "registration": registration,
            "participants": participants,
            "course":course, 
        }
    )

@login_required
def my_events_view(request):
    registrations = (
        Registration.objects
        .filter(user=request.user)
        .select_related("course", "course__event")
        .order_by("-registered_at")
    )

    return render(
        request,
        "my_events.html",
        {"registrations": registrations}
    )
# def registration_lookup_form(request):
#     if request.method == "POST":
#         code = request.POST.get("code")
#         return redirect("registration_lookup", code=code)

#     return render(request, "registration_lookup_form.html")