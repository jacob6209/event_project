import datetime
from datetime import datetime
from django.http import Http404
from django.shortcuts import render, get_object_or_404,redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from event.utils import serialize_course_data
from .models import Participant, RegisteredParticipant, Registration, Course,Guest,EventType
from django.contrib.auth.decorators import login_required
from .forms import CourseDateFormSet, ParticipantActiveForm,GuestForm,GuestEditForm\
     , EventTypeForm, EventForm, CourseFormSet,Event,CourseDateForm
from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory
from django.db.models import Prefetch

# stuff View


def index(request):
    event_types = EventType.objects.prefetch_related(
        Prefetch(
            "events",
            queryset=Event.objects.filter(is_publish=True).prefetch_related("courses")
        )
    ).order_by("-id")

    context = {
        "event_types": event_types
    }
    return render(request, "index.html", context)

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
    
    # User must come from event_type_step
    if not request.session.get("event_type_new_title"):
        return redirect("event_type_step")

    prefill = {}

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "prev":
            # Save POSTed values into session before going back
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
        has_error = False
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

        # ===== Prepare prefill for template =====
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

        # ===== Store in session =====
        request.session["event_title"] = title
        request.session["event_rules"] = rules
        request.session["event_is_multi_course"] = is_multi_course
        request.session["event_has_food"] = has_food
        request.session["event_allows_guests"] = allows_guests
        request.session["event_requires_approval"] = requires_approval
        request.session["event_max_capacity"] = max_capacity
        request.session["event_max_guests"] = max_guests
        request.session["event_max_guests_per_user"] = max_guests_per_user

        # ===== Handle image upload =====
        if "image" in request.FILES:
            image = request.FILES["image"]
            saved_name = default_storage.save(image.name, ContentFile(image.read()))
            request.session["event_image_name"] = saved_name  # now points to actual file in MEDIA_ROOT

        return redirect("wizard_course")

    # ===== GET ===== prefill from session =====
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
        "image_name": request.session.get("event_image_name"),
    }

    return render(request, "step_event.html", {"step": 2, "prefill": prefill})

@login_required
def course_step(request):
    if not request.user.is_staff:
        return redirect("index")

    if "event_is_multi_course" not in request.session:
        return redirect("event_step")

    is_multi_course = request.session.get("event_is_multi_course", False)

    # Always at least 1 empty form
    CourseFormSet = modelformset_factory(
        Course,
        form=CourseDateForm,
        extra=1,
        can_delete=True,
    )

    if request.method == "POST":
        if request.POST.get("action") == "prev":
            return redirect("wizard_event")

        formset = CourseFormSet(request.POST, queryset=Course.objects.none())

        # Force validation for all forms
        for form in formset.forms:
            form.empty_permitted = False

        if formset.is_valid():
            # Ensure at least one non-deleted form
            has_data = any(form.cleaned_data and not form.cleaned_data.get("DELETE")
                           for form in formset.forms)
            if not has_data:
                messages.error(request, "لطفاً حداقل یک دوره را پر کنید")
                return render(request, "step_course.html",
                              {"formset": formset, "is_multi_course": is_multi_course, "step": 3})

            courses = formset.save(commit=False)
            if is_multi_course and len(courses) < 2:
                messages.error(request, "در حالت چند دوره‌ای باید حداقل دو دوره ایجاد شود")
                return render(request, "step_course.html",
                              {"formset": formset, "is_multi_course": is_multi_course, "step": 3})

            # Save cleaned data to session
            request.session["courses_data"] = [
                serialize_course_data(form.cleaned_data)
                for form in formset.forms
                if form.cleaned_data and not form.cleaned_data.get("DELETE")
                ]
            request.session.modified = True
            return redirect("confirm_step")

    else:
        # GET request → just create empty formset
        formset = CourseFormSet(queryset=Course.objects.none())

        # for form in formset.forms:
        #     form.empty_permitted = False

    return render(request, "step_course.html",
                  {"formset": formset, "is_multi_course": is_multi_course, "step": 3})
@login_required
def confirm_step(request):

    if not request.user.is_staff:
        return redirect("index")

    # Check required session data
    if not request.session.get("event_type_new_title"):
        return redirect("wizard_event_type")
    if not request.session.get("event_title"):
        return redirect("wizard_event")
    if not request.session.get("courses_data"):
        return redirect("wizard_course")

    # Collect all prefill data
    prefill = {
        "event_type": request.session.get("event_type_new_title"),
        "event": {
            "title": request.session.get("event_title"),
            "rules": request.session.get("event_rules"),
            "is_multi_course": request.session.get("event_is_multi_course", False),
            "has_food": request.session.get("event_has_food", False),
            "allows_guests": request.session.get("event_allows_guests", False),
            "requires_approval": request.session.get("event_requires_approval", False),
            "max_capacity": request.session.get("event_max_capacity", 10),
            "max_guests": request.session.get("event_max_guests", 0),
            "max_guests_per_user": request.session.get("event_max_guests_per_user", 0),
            "image_name": request.session.get("event_image_name"),
        },
        "courses": request.session.get("courses_data", [])
    }

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "prev_event_type":
            return redirect("wizard_event_type")
        elif action == "prev_event":
            return redirect("wizard_event")
        elif action == "prev_course":
            return redirect("wizard_course")
        elif action in ["save", "save_publish"]:

            is_publish = (action == "save_publish")

            # helper function (OUTSIDE loop)
            def parse_date(date_str):
                return datetime.fromisoformat(date_str).date() if date_str else None

            try:
                with transaction.atomic():
                    event_type, _ = EventType.objects.get_or_create(
                        name=prefill["event_type"]
                    )

                    event = Event.objects.create(
                        event_type=event_type,
                        title=prefill["event"]["title"],
                        rules=prefill["event"]["rules"],
                        is_multi_course=prefill["event"]["is_multi_course"],
                        has_food=prefill["event"]["has_food"],
                        allows_guests=prefill["event"]["allows_guests"],
                        requires_approval=prefill["event"]["requires_approval"],
                        max_capacity=prefill["event"]["max_capacity"],
                        max_guests=prefill["event"]["max_guests"],
                        max_guests_per_user=prefill["event"]["max_guests_per_user"],
                        image=request.session.get("event_image_file"),
                        is_publish=is_publish,
                    )
                    for course_data in prefill["courses"]:
                        Course.objects.create(
                            event=event,
                            title=course_data.get("title"),
                            start_date=parse_date(course_data.get("start_date")),
                            end_date=parse_date(course_data.get("end_date")),
                            registration_start=parse_date(course_data.get("registration_start")),
                            registration_end=parse_date(course_data.get("registration_end")),
                            max_capacity=course_data.get("max_capacity"),
                            is_publish=is_publish,
                        )

            except Exception as e:
                print(f'{e}')
                messages.error(
                    request,
                    "خطا در ذخیره اطلاعات. لطفاً دوباره تلاش کنید."
                )
                return redirect("wizard_confirm")

            for key in [
                "event_type_new_title",
                "event_title",
                "event_rules",
                "event_is_multi_course",
                "event_has_food",
                "event_allows_guests",
                "event_requires_approval",
                "event_max_capacity",
                "event_max_guests",
                "event_max_guests_per_user",
                "event_image_name",
                "event_image_file",
                "courses_data",
            ]:
                request.session.pop(key, None)

            messages.success(request, "اطلاعات با موفقیت ثبت شد.")
            return redirect("index")
                
    return render(request, "confirm_step.html", {"step":4,"prefill": prefill})

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