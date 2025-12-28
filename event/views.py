from django.http import Http404
from django.shortcuts import render, get_object_or_404,redirect
from .models import Participant, RegisteredParticipant, Registration, Course,Guest,EventType
from django.contrib.auth.decorators import login_required
from .forms import ParticipantActiveForm,GuestForm,GuestEditForm\
     , EventTypeForm, EventForm, CourseFormSet,Event
from django.contrib import messages
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required

# stuff View

@login_required
def staff_events(request):
    if not request.user.is_staff:
        messages.error(request, "شما اجازه دسترسی به این صفحه را ندارید.")
        return render(request, "registration_not_found.html")
    return render(request,"staff_events.html")

def staff_add_event(request):
    if request.method == "POST":
        # Check if creating a new EventType
        if "new_event_type" in request.POST:
            event_type_form = EventTypeForm(request.POST, prefix="type")
            if event_type_form.is_valid():
                event_type = event_type_form.save()
        else:
            event_type_id = request.POST.get("event_type")
            event_type = EventType.objects.get(id=event_type_id)

        event_form = EventForm(request.POST, prefix="event")
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.event_type = event_type
            event.save()

            # Only show courses if multi-course
            if event.is_multi_course:
                course_formset = CourseFormSet(request.POST, instance=event, prefix="course")
                if course_formset.is_valid():
                    course_formset.save()
            return redirect("staff_event_list")
    else:
        event_type_form = EventTypeForm(prefix="type")
        event_form = EventForm(prefix="event")
        course_formset = CourseFormSet(prefix="course")

    return render(request, "staff_add_event.html", {
        "event_type_form": event_type_form,
        "event_form": event_form,
        "course_formset": course_formset,
        "event_types": EventType.objects.all()
    })
# use wizard 
@login_required
def event_type_step(request):

    if not request.user.is_staff:
        return redirect("index")

    prefill = {
        "name": request.session.get("event_type_new_title", "")
    }

    if request.method == "POST":
        new_title = request.POST.get("new_title", "").strip()


        if  not new_title:
            return render(request, "step_event_type.html", {
                "step": 1,
                "error": "ورود عنوان اجباری است"
            })

        request.session["event_type_new_title"] = new_title

        prefill={
            "name": request.session.get("event_type_new_title", ""),
        }
        if EventType.objects.filter(name=new_title).exists():
            return render(request, "step_event_type.html", {
                "step": 1,
                "error": "دسته بندی با این نام قبلا ثبت شده است."
            })

        return redirect("wizard_event")
        
    return render(request, "step_event_type.html", {
        "step": 1,
        "prefill": prefill
    })

@login_required
def event_step(request):
    if not request.user.is_staff:
        return redirect("index")
    
    # user must come from event_type_step
    if not request.session.get("event_type_new_title"):
        return redirect("event_type_step")

    prefill = {}  # dictionary to pass to template

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "prev":
            request.session["event_title"] = request.POST.get("title", "")
            request.session["event_rules"] = request.POST.get("rules", "")
            request.session["event_is_multi_course"] = bool(request.POST.get("is_multi_course"))
            request.session["event_has_food"] = bool(request.POST.get("has_food"))
            request.session["event_allows_guests"] = bool(request.POST.get("allows_guests"))
            request.session["event_requires_approval"] = bool(request.POST.get("requires_approval"))
            request.session["event_max_capacity"] = int(request.POST.get("max_capacity") or 10)
            request.session["event_max_guests"] = int(request.POST.get("max_guests") or 0)
            request.session["event_max_guests_per_user"] = int(request.POST.get("max_guests_per_user") or 0)
           
            return redirect("wizard_event_type")

        has_error = False

        # ===== Extract fields =====
        title = request.POST.get("title", "").strip()
        rules = request.POST.get("rules", "").strip()
        is_multi_course = bool(request.POST.get("is_multi_course"))
        has_food = bool(request.POST.get("has_food"))
        allows_guests = bool(request.POST.get("allows_guests"))
        requires_approval = bool(request.POST.get("requires_approval"))
        max_capacity = int(request.POST.get("max_capacity") or 10)
        max_guests = int(request.POST.get("max_guests") or 0)
        max_guests_per_user = int(request.POST.get("max_guests_per_user") or 0)

        # ===== Validation =====
        if not title:
            messages.error(request, "برای ایجاد رویداد جدید، وارد کردن عنوان الزامی است")
            has_error = True
        if allows_guests and max_guests == 0:
            messages.error(request, "در صورت پذیرش مهمان، ظرفیت مهمان نمی‌تواند صفر باشد")
            has_error = True
        if max_guests_per_user > max_guests:
            messages.error(request, "حداکثر مهمان هر کاربر نمی‌تواند بیشتر از کل ظرفیت مهمان باشد")
            has_error = True
        if not allows_guests and max_guests > 0:
            allows_guests = True

        # ===== Prepare prefill from POST so form keeps data =====
        prefill = {
            "title": title,
            "rules": rules,
            "is_multi_course": is_multi_course,
            "has_food": has_food,
            "allows_guests": allows_guests,
            "requires_approval": requires_approval,
            "max_capacity": max_capacity,
            "max_guests": max_guests,
            "max_guests_per_user": max_guests_per_user,
        }

        if has_error:
            return render(request, "step_event.html", {"step": 2, "prefill": prefill})

        # ===== Store in session (safe, only if no error) =====
        request.session["event_title"] = title
        request.session["event_rules"] = rules
        request.session["event_is_multi_course"] = is_multi_course
        request.session["event_has_food"] = has_food
        request.session["event_allows_guests"] = allows_guests
        request.session["event_requires_approval"] = requires_approval
        request.session["event_max_capacity"] = max_capacity
        request.session["event_max_guests"] = max_guests
        request.session["event_max_guests_per_user"] = max_guests_per_user

        # ===== Image (temporary) =====
        if "image" in request.FILES:
            request.session["event_image_name"] = request.FILES["image"].name

        return redirect("wizard_confirm")

    # ===== GET ===== use prefilled session data if no POST =====
    prefill = {
        "title": request.session.get("event_title", ""),
        "rules": request.session.get("event_rules", ""),
        "is_multi_course": request.session.get("event_is_multi_course", False),
        "has_food": request.session.get("event_has_food", False),
        "allows_guests": request.session.get("event_allows_guests", False),
        "requires_approval": request.session.get("event_requires_approval", False),
        "max_capacity": request.session.get("event_max_capacity", 10),
        "max_guests": request.session.get("event_max_guests", 0),
        "max_guests_per_user": request.session.get("event_max_guests_per_user", 0),
    }

    return render(request, "step_event.html", {"step": 2, "prefill": prefill})


# ------------------------------------------------
# User View
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
            guest = form.save(commit=False)
            print ("im here ..1..")
            if not guest.registration:
                print ("im here ..2..")
                messages.error(request, "لطفا یک دوره را انتخاب کنید")
                return redirect('registration_guest')
            guest.save()
            messages.success(request, "اطلاعات مهمان جدید با موفقیت ثبت شد")
            return redirect(guest.registration.get_absolute_url())
        
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
def delete_guest(request, guest_id):
    try:
        guest = Guest.objects.get(
            id=guest_id,
            registration__user=request.user,
            status="pending"
        )
        if request.method =='GET': 
            guest.delete()
            messages.success(request, 'مهمان با موفقیت حذف شد.')
    except Guest.DoesNotExist:
        messages.error(request, 'مهمان مورد نظر یافت نشد یا شما دسترسی لازم برای حذف آن را ندارید.')
        
    return redirect(guest.get_absolute_url())
           
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
    try:
        registration = get_object_or_404(
            Registration,
            id=registration_id,
            user=user,
            status="pending"
        )
    except Http404:
        return render(
            request,
            "registration_not_found.html",
            status=404
        )


    participants = Participant.objects.filter(user=user, is_active=True)
    participants_count=participants.count()
    courses = Course.objects.all()
    guests=Guest.objects.filter(registration=registration)

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
    # guest_forms=[
    #     (g,GuestForm(
    #         prefix=str(g.id),
    #         instance=g
    #     ))
    #     for g in guests
    # ]
    guest_forms = [
        (g, GuestEditForm(prefix=str(g.id), instance=g, user=request.user))
        for g in guests
    ]
    # ToDo i have to Handle Unexpected Error 
    if request.method == "POST":
        selected_course_id = request.POST.get("course")
        if not selected_course_id:
            return render(request, "reregistration.html", {
                "participants_count": participants_count,
                "participant_forms": participant_forms,
                "guest_forms": guest_forms,
                "courses": courses,
                "is_edit": True,
                "selected_course": selected_course,
                "error": "لطفا یک دوره انتخاب کنید."
            })

        selected_course = get_object_or_404(Course, id=selected_course_id)
        selected_event_type = selected_course.event.event_type

        #  Prevent duplicate registration for the same event type (exclude current registration)
        already_registered = Registration.objects.filter(
            user=user,
            course__event__event_type=selected_event_type
        ).exclude(id=registration.id).exists()

        if already_registered:
            messages.error(
                request,
                "⚠️ شما قبلاً در این رویداد ثبت‌نام کرده‌اید. امکان ثبت‌نام مجدد وجود ندارد."
            )
                
            context={
                'participant_forms': participant_forms,
                "guest_forms": guest_forms,
                'courses': courses,
                "registration": registration,
                "is_edit": True,
                "error": "⚠️ شما قبلاً در این رویداد ثبت‌نام کرده‌اید. امکان ثبت‌نام دوباره وجود ندارد.",
                'selected_course': selected_course,
            }
            return render(request, 'reregistration.html',context)
        bound_participant_forms = []
        bound_guest_forms = []
        has_error = False
        with transaction.atomic():
            # Update registration 
            registration.course = selected_course
            registration.save(update_fields=["course"]) 

            # Update participant forms
            for p, _ in participant_forms:
                form = ParticipantActiveForm(
                    request.POST,
                    prefix=str(p.id),
                    instance=p
                )
                bound_participant_forms.append((p, form))
                if form.is_valid():
                    is_reserved = form.cleaned_data["is_reserved"]

                    RegisteredParticipant.objects.update_or_create(
                        registration=registration,
                        participant=p,
                        defaults={"is_reserved": is_reserved}
                    )
            # Update guest forms
            for g, _ in guest_forms:
                form = GuestEditForm(request.POST, prefix=str(g.id), instance=g, user=request.user)
                
                bound_guest_forms.append((g, form))
                if form.is_valid():
                    guest = form.save(commit=False)
                    guest.registration = registration 
                    guest.save()
                else:
                    has_error = True
                    for error in form.non_field_errors():
                        messages.error(request, error)
                
        if has_error:
            return render(request, "reregistration.html", {
                "participant_forms": bound_participant_forms,
                "guest_forms": bound_guest_forms,
                # "participant_forms": participant_forms,
                # "guest_forms": guest_forms,
                "courses": courses,
                "participants_count" : participants_count,
                "selected_course": selected_course,
                "registration": registration,
                "is_edit": True,
            })
        
        messages.success(request, "✅ اطلاعات ثبت‌نام با موفقیت ویرایش یافت")
        return redirect(
            "registration_lookup",
            code=registration.transaction_id
        )
    return render(request, "reregistration.html", {
            "participant_forms": participant_forms,
            "guest_forms": guest_forms,
            "courses": courses,
            "participants_count" : participants_count,
            "selected_course": selected_course,
            "registration": registration,
            "is_edit": True,
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
        
        # CHECK CAPACITY
        participants_count = RegisteredParticipant.objects.filter(
            registration__course=selected_course
        ).count()

        guests_count = Guest.objects.filter(
            registration__course=selected_course,
            is_reserved=True
        ).count()

        if participants_count + guests_count >= selected_course.max_capacity:
            messages.error(
                request,
                "ظرفیت این دوره تکمیل شده است."
            )
            return render(request, 'reregistration.html', {
                'participant_forms': participant_forms,
                'courses': courses,
            })
        with transaction.atomic():
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
        guests = Guest.objects.filter(registration=registration)
        course=registration.course
        participants_count = participants.count()
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
            "guests": guests,
            "participants_count":participants_count,
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