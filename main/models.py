from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return f"{self.username or self.first_name or self.id} ({self.role})"


# ----- Unified Course model -----
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="courses/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=now)
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


# ----- Materials -----
class Material(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    COURSE_CONTENT_TYPES = [
        ('pdf', 'PDF'),
        ('video', 'Video'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    # course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=10, choices=COURSE_CONTENT_TYPES)
    file = models.FileField(upload_to='modules/')
    completion = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class SMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    # course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/')

    class Meta:
        verbose_name = "Materilas"
        verbose_name_plural = "Materials"

    def __str__(self):
        return f"{self.course.title} - {self.title}"
  
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    profile_image = models.ImageField(
        upload_to="student_profiles/",
        blank=True,
        null=True,
        default="student_profiles/default.png"
    )

    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    COURSE_DURATION_CHOICES = [
        ('2 - Months', '2 - Months'),
        ('1 - Month', '1 - Month'),
        ('1 - Week', '1 - Week'),
    ]

    COURSE_TIMING_CHOICES = [
        ('11:00 AM - 2:00 PM', '11:00 AM - 2:00 PM'),
        ('3:00 PM - 6:00 PM', '3:00 PM - 6:00 PM '),
        ('6:00 PM - 9:00 PM', '6:00 PM - 9:00 PM'),
        ('6:30 PM - 9:30 PM', '6:30 PM - 9:30 PM'),
    ]

    END_GOAL_CHOICES = [
        ('To became a freelancer', 'To became a freelancer'),
        ('To Study Marketing for own business', 'To Study Marketing for own business'),
        ('For job', 'For job'),
        ('For career growth','For career growth'),
    ]

    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    course_duration = models.CharField(max_length=50, choices=COURSE_DURATION_CHOICES, blank=True, null=True)
    course_timing = models.CharField(max_length=50, choices=COURSE_TIMING_CHOICES, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    company_college = models.CharField(max_length=255, blank=True, null=True)
    end_goal = models.CharField(max_length=50, choices=END_GOAL_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Staff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username or self.user.first_name

# -----------------------
# # Signals: auto-create profile & sync email
# # -----------------------

# ----- Signals -----
@receiver(post_save, sender=User)
def create_or_update_profiles(sender, instance, created, **kwargs):
    """
#     When a User is created:
#       - if role == 'student' create Student profile if missing and copy email
#       - if role == 'staff' create Staff profile if missing and copy email

#     Also
    """
    if created:
        if getattr(instance, "role", None) == "student":
            Student.objects.create(user=instance, email=instance.email)
        elif getattr(instance, "role", None) == "staff":
            Staff.objects.create(user=instance, email=instance.email)

    try:
        if getattr(instance, "role", None) == "student":
            student = Student.objects.filter(user=instance).first()
            if student and student.email != instance.email:
                student.email = instance.email
                student.save(update_fields=['email'])
    except:
        pass

    try:
        if getattr(instance, "role", None) == "staff":
            staff = Staff.objects.filter(user=instance).first()
            if staff and staff.email != instance.email:
                staff.email = instance.email
                staff.save(update_fields=['email'])
    except:
        pass


# ----- Certificate & Tasks -----
class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='certificates/')
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}"


class Task(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_submissions/')
    drive_file_url = models.URLField(blank=True, null=True)
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.task.title}"
    



# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta

class AttendancePeriod(models.Model):
    """
    Represents the attendance date-range for one or more students.
    Admin will create/edit this; saving auto-creates Attendance rows for each date × student.
    """
    # Keep the old single-student FK while migrating OR remove if you prefer immediate switch.
    # If you already want only multi-student behavior, remove the old `student` field and
    # use only the `students` M2M. Below we add the M2M as `students`.
    # student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='attendance_periods')  # (OPTIONAL during migration)

    students = models.ManyToManyField('Student', related_name='attendance_periods', blank=True)

    course = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave empty if course hasn't ended yet")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Attendance Period"
        verbose_name_plural = "Attendance & Periods"
        ordering = ['-start_date']

    def __str__(self):
        # show count to make admin listing useful
        student_count = self.students.count() if self.pk else 0
        return f"Attendance ({self.start_date} → {self.end_date or 'ongoing'}) for {student_count} student(s)"

    def period_end_for_calculation(self):
        return self.end_date or date.today()

    def all_dates(self):
        end = self.period_end_for_calculation()
        cur = self.start_date
        dates = []
        while cur <= end:
            dates.append(cur)
            cur = cur + timedelta(days=1)
        return dates

    def regenerate_attendance_rows(self):
        """Create/get Attendance rows for every student in the period, for every date in the period."""
        from .models import Attendance
        students = list(self.students.all())
        if not students:
            # if you kept old single-student FK for migration compatibility:
            try:
                # if `student` exists as an attribute, include it
                if hasattr(self, 'student') and self.student:
                    students = [self.student]
            except Exception:
                students = []
        for d in self.all_dates():
            for st in students:
                Attendance.objects.get_or_create(
                    period=self,
                    student=st,
                    date=d,
                    defaults={
                        'status': Attendance.STATUS_UNMARKED,
                        'marked_by': None,
                    }
                )


class Attendance(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_HOLIDAY = 'holiday'
    STATUS_UNMARKED = 'unmarked'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_HOLIDAY, 'Holiday'),
        (STATUS_UNMARKED, 'Unmarked'),
    ]

    # ✅ REQUIRED FOR ADMIN INLINE (THIS WAS MISSING)
    period = models.ForeignKey(
        AttendancePeriod,
        on_delete=models.CASCADE,
        related_name='daily_attendance'
    )

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='attendances'
    )

    date = models.DateField(db_index=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_UNMARKED)
    note = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date', 'period')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} — {self.date} — {self.get_status_display()}"

