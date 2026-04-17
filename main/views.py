from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .forms import RegisterForm, EditProfileForm
from .models import User
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import user_passes_test
from .models import Course, Material
from django.shortcuts import render, get_object_or_404, HttpResponse
from .models import Student, SMaterial, Certificate, Task, TaskSubmission, Module
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Student, User
from .google_drive import upload_to_drive
from django.http import FileResponse, Http404
import mimetypes
from django.http import HttpResponseForbidden




def course_overview(request):
    courses = Course.objects.all()
    return render(request, "course_overview.html", {"courses": courses})
def admin_panel(request):
    materials = Material.objects.all().order_by('-uploaded_at')
    return render(request, 'admin_panel.html', {'materials': materials})

def certificates(request):
    return render(request, "certificates.html")

def home(request):
    # 6 success stories
    success_stories = [
        {
            "first_name": "Vishnu",
            "last_name": "Rathinasamy",
            "title": "Software Engineer",
            "description": "Transformed career with coding skills.",
            "profile_pic": "images/profile1.jpg",
            "icon": "⭐",
            "content": "Top Performer"
        },
        {
            "first_name": "Rahul",
            "last_name": "Sharma",
            "title": "Data Scientist",
            "description": "Learned AI and ML.",
            "profile_pic": "images/profile2.jpg",
            "icon": "🔥",
            "content": "Innovator"
        },
        {
            "first_name": "Anita",
            "last_name": "Singh",
            "title": "UX Designer",
            "description": "Mastered UI/UX skills.",
            "profile_pic": "images/profile3.jpg",
            "icon": "💡",
            "content": "Creative Mind"
        },
        {
            "first_name": "Karan",
            "last_name": "Patel",
            "title": "Marketing Expert",
            "description": "Boosted sales by 300%.",
            "profile_pic": "images/profile4.jpg",
            "icon": "🚀",
            "content": "Leader"
        },
        {
            "first_name": "Priya",
            "last_name": "Kumar",
            "title": "Entrepreneur",
            "description": "Started own tech company.",
            "profile_pic": "images/profile5.jpg",
            "icon": "🏆",
            "content": "Achiever"
        },
        {
            "first_name": "Sahil",
            "last_name": "Verma",
            "title": "Full Stack Developer",
            "description": "Built multiple web apps.",
            "profile_pic": "images/profile6.jpg",
            "icon": "💻",
            "content": "Tech Guru"
        },
    ]

    return render(request, 'home.html', {
        'success_stories': success_stories
    })


@login_required
def register(request):
    # Only allow admin or superuser to access this page
    if not (request.user.is_superuser or getattr(request.user, "role", None) == "admin"):
        return render(request, "403.html", status=403)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Auto-activate if admin creates the user
            if request.user.is_superuser or getattr(request.user, "role", None) == "admin":
                user.is_active = True
            else:
                user.is_active = False  # normal users need email verification

            user.save()

            if not user.is_active:
                # Send email verification
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verify_url = request.build_absolute_uri(
                    reverse("activate", kwargs={"uidb64": uid, "token": token})
                )
                subject = "Activate your account"
                message = render_to_string("emails/activate_email.txt", {
                    "user": user,
                    "verify_url": verify_url,
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                messages.success(request, "Account created. Please check your email to activate.")
            else:
                messages.success(request, "User created successfully!")

            # Redirect admin back to the admin panel after creating user
            return redirect("admin_panel")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Activation successful. You can now login.")
        return redirect("login")
    else:
        messages.error(request, "Activation link invalid or expired.")
        return redirect("home")

# ---------- Login / Logout ----------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            # --- SUPERUSER FIX ---
            auth_login(request, user)
            if user.is_superuser or user.role in ["admin", "staff"]:
                return redirect("/admin/")
            
            return redirect("student_panel")

        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def logout_view(request):
    auth_logout(request)
    return redirect("home")

# ---------- Dashboards ----------
# @login_required
# def admin_panel(request):
#     # ✅ Permission check
#     if request.user.is_superuser or (
#         hasattr(request.user, "role") and request.user.role == "admin"
#     ):
#         # ✅ Fetch materials and send to template
#         materials = Material.objects.all().order_by('-uploaded_at')
#         return render(request, "admin_panel.html", {'materials': materials})

#     # ❌ If not authorized
#     return render(request, "403.html", status=403)


@login_required
def staff_panel(request):
    if request.user.role not in ("staff", "admin"):
        return render(request, "403.html", status=403)
    return render(request, "staff_panel.html")

@login_required
def student_panel(request):
    pass
    print(request.user.role)
    if request.user.role != "student":
        return render(request, "403.html", status=403)
    return render(request, "student_panel.html")

# ---------- Profile ----------
@login_required
def profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, "profile.html", {"form": form})


def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated. You can now login.")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid.")
        return redirect("home")

@login_required
def student_panel(request):
    print(request.user)
    students = Student.objects.all()
    print(students)
    print(request.user)
    user = get_object_or_404(User, pk=request.user.id)
    courses = Course.objects.all()
    materials = SMaterial.objects.all()
    if user.role == "student": 
        certificates = Certificate.objects.filter(student__user=user)
    else:
        certificates = Certificate.objects.none()
    tasks = Task.objects.all()

    context = {
        'student': user,
        'students': students,
        'courses': courses,
        'materials': materials,
        'certificates': certificates,
        'tasks': tasks,
    }
    return render(request, 'student_panel.html', context)


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'student_detail.html', {'student': student})

@csrf_exempt
def add_student(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            name = name.strip()
        email = data.get('email')
        phone = data.get('phone')
        course = data.get('course')

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

    
        # Create user
        user, created = User.objects.get_or_create(
            username=name.replace(" ", ""),
            defaults={
                'first_name': name.split()[0] if name else '',
                'last_name': ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                'email': email
            }
        )

        # Create student profile
        Student.objects.get_or_create(
            user=user,
            defaults={
                'phone': phone,
                'course': course
            }
        )

        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)

def course_list(request):
    courses = Course.objects.prefetch_related('modules').all()
    return render(request, 'main/courses.html', {'courses': courses})


@login_required  # optional: require login to view materials
def materials_page(request):
    # get all courses with prefetch of materials to avoid N+1
    courses = Course.objects.prefetch_related('materials').all()
    context = {'courses': courses}
    return render(request, 'student_panel/s_materials.html', context)

@login_required
def material_preview(request, pk):
    """
    Serves the file with Content-Disposition inline so the browser displays it.
    Does not remove the possibility of download — see notes below.
    """
    material = get_object_or_404(SMaterial, pk=pk)
    file_path = material.file.path
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    try:
        response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
        # set inline disposition
        response['Content-Disposition'] = f'inline; filename="{material.title}.pdf"'
        return response
    except FileNotFoundError:
        raise Http404("File not found")

def submit_task(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("submission")
        if not uploaded_file:
            messages.error(request, "No file selected.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Get Student instance
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Get Task instance from POST data (make sure task_id is sent in the form)
        task_id = request.POST.get("task_id")
        if not task_id:
            messages.error(request, "No task selected.")
            return redirect(request.META.get("HTTP_REFERER", "/"))
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            messages.error(request, "Task not found.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Create the TaskSubmission instance
        submission = TaskSubmission.objects.create(
            student=student,
            task=task,
            file=uploaded_file,
            original_filename=uploaded_file.name  # <-- your line added here
        )

        # Upload file to Google Drive and save the link
        try:
            drive_link = upload_to_drive(uploaded_file, uploaded_file.name)
            submission.drive_file_url = drive_link
            submission.save()
            messages.success(request, "File uploaded successfully!")
        except Exception as e:
            submission.delete()
            messages.error(request, f"Upload failed: {e}")

    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def student_panel(request):

    # ✅ Allow only these roles
    if request.user.role not in ["student", "admin", "staff"]:
        return HttpResponseForbidden("Access denied")

    student = None
    courses = Course.objects.none()
    materials = SMaterial.objects.none()
    tasks = Task.objects.none()
    certificates = Certificate.objects.none()

    # ✅ SAFE lookup (will NOT crash)
    if request.user.role == "student":
        student = Student.objects.filter(user=request.user).first()

        if student and student.course:
            course = student.course

            courses = Course.objects.filter(id=course.id)
            materials = SMaterial.objects.filter(course=course)
            tasks = Task.objects.filter(course=course)
            certificates = Certificate.objects.filter(student=student, course=course)

    context = {
        'students': [student] if student else [],
        'courses': courses,
        'materials': materials,
        'certificates': certificates,
        'tasks': tasks,
    }

    return render(request, 'student_panel.html', context)

def module_preview(request, pk):
    try:
        module = Module.objects.get(pk=pk)
        return FileResponse(
            module.file.open(),
            content_type="application/pdf"
        )
    except:
        raise Http404()
    
from django.http import FileResponse, Http404
import os


    # main/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, Student, Course

@csrf_exempt
def add_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            username = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            course_title = data.get('course')  # corrected
            course_duration = data.get('course_duration')
            course_timing = data.get('course_timing')
            location = data.get('location')
            occupation = data.get('occupation')
            company_college = data.get('company_college')
            end_goal = data.get('end_goal')

            # Create or get user using custom User
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'role': 'student'}
            )

            # Get or create course using title
            course, _ = Course.objects.get_or_create(title=course_title)

            # Create or update student
            student, created = Student.objects.update_or_create(
                user=user,
                defaults={
                    'phone': phone,
                    'course': course,
                    'course_duration': course_duration,
                    'course_timing': course_timing,
                    'location': location,
                    'occupation': occupation,
                    'company_college': company_college,
                    'end_goal': end_goal
                }
            )

            return JsonResponse({'status': 'success', 'message': 'Student added successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'})


from django.shortcuts import render, get_object_or_404, redirect

def student_photo_edit(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == "POST" and request.FILES.get("profile_image"):
        student.profile_image = request.FILES["profile_image"]
        student.save()
        return redirect("student_detail", student.id)

    return render(request, "student_photo_edit.html", {"student": student})

from django.shortcuts import render, get_object_or_404
from datetime import date, timedelta
from .models import Student, AttendancePeriod, Attendance 
from django.contrib.auth.decorators import login_required
# views.py
from django.shortcuts import render
from .models import Student
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student, AttendancePeriod, Attendance, Course, SMaterial, Task, Certificate



@login_required
def student_panel(request):
    student = get_object_or_404(Student, user=request.user)

    courses = Course.objects.filter(student=student)
    materials = SMaterial.objects.filter(course__in=courses)
    tasks = Task.objects.filter(course__in=courses)
    certificates = Certificate.objects.filter(student=student)

    # ✅ ATTENDANCE PERIOD
    period = AttendancePeriod.objects.filter(students=student).order_by('-start_date').first()

    rows = []
    present_count = 0
    class_days = 0
    attendance_percent = 0

    attendance = Attendance.objects.none()

    if period:
        start = period.start_date
        end = period.period_end_for_calculation()

        dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        attendance_qs = Attendance.objects.filter(period=period, date__range=(start, end), student=student)
        attendance_map = {a.date: a for a in attendance_qs}

        for i, d in enumerate(dates):
            att = attendance_map.get(d)
            status = att.status if att else Attendance.STATUS_UNMARKED

            if status != Attendance.STATUS_HOLIDAY and status != Attendance.STATUS_UNMARKED:
                class_days += 1
            if status == Attendance.STATUS_PRESENT:
                present_count += 1

            rows.append({
                'index': i + 1,
                'date': d,
                'status': status,
                'status_display': att.get_status_display() if att else 'Unmarked',
                'note': att.note if att else '',
            })

        attendance_percent = round((present_count / class_days) * 100, 2) if class_days else 0
        attendance = Attendance.objects.filter(period=period, student=student)

    # ✅ Precompute events for FullCalendar
    events = []

    for task in tasks:
        events.append({
            "title": task.title,
            "start": task.due_date.isoformat(),
            "color": "#0051ff",
            "display": "background" ,
            # "classNames": ["attendance-event"]
            "extendedProps": {
                "description": task.description if hasattr(task, "description") else "",
            }
        })


    for att in attendance:
        color = "gray"
        if att.status == Attendance.STATUS_PRESENT:
            color = "green"
        elif att.status == Attendance.STATUS_ABSENT:
            color = "red"
        elif att.status == Attendance.STATUS_HOLIDAY:
            color = "orange"

        # events.append({
        #     "title": att.get_status_display(),
        #     "start": att.date.isoformat(),
        #     "color": color
        # })
        events.append({
            "title": att.get_status_display(),
            "start": att.date.isoformat(),
            "display": "background",  # ← key: renders the entire day cell
            "color": color
        })


    context = {
        "student": student,
        "courses": courses,
        "materials": materials,
        "tasks": tasks,
        "certificates": certificates,
        "attendance": attendance,
        "period": period,
        "rows": rows,
        "present_count": present_count,
        "class_days": class_days,
        "attendance_percent": attendance_percent,
        "events": events,  # ✅ pass events to template
    }

    return render(request, "student_panel.html", context)

# views.py



@login_required
def student_attendance_view(request, student_id=None):
    user = request.user

    # Fetch the student object for this user
    if student_id and user.is_staff:
        student = get_object_or_404(Student, pk=student_id)
    else:
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            return render(request, 'student/attendance_fragment.html', {
                'student': None,
                'period': None
            })

    # Fetch the latest attendance period
    period = AttendancePeriod.objects.filter(students=student).order_by('-start_date').first()
    print("Period",period)

    if not period:
        return render(request, 'student/attendance_fragment.html', {
            'student': student,
            'period': None
        })

    # 4️⃣ Generate attendance table
    start = period.start_date
    end = period.period_end_for_calculation()
    dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    attendance_qs = Attendance.objects.filter(period=period, date__range=(start, end))
    attendance_map = {a.date: a for a in attendance_qs}

    rows = []
    present_count = 0
    class_days = 0
    for i, d in enumerate(dates):
        att = attendance_map.get(d)
        status = att.status if att else Attendance.STATUS_UNMARKED
        if status != Attendance.STATUS_HOLIDAY and status != Attendance.STATUS_UNMARKED:
            class_days += 1
        if status == Attendance.STATUS_PRESENT:
            present_count += 1
        rows.append({
            'index': i + 1,
            'date': d,
            'status': status,
            'status_display': att.get_status_display() if att else 'Unmarked',
            'note': att.note if att else '',
        })

    attendance_percent = round((present_count / class_days) * 100, 2) if class_days else 0


    # 5️⃣ Pass context to template
    return render(request, 'student/attendance_fragment.html', {
        'student': student,
        'period': period,
        'rows': rows,
        'present_count': present_count,
        'class_days': class_days,
        'attendance_percent': attendance_percent,
    })



