# from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# from .models import User, Course
# from .models import Student, SCourse, SMaterial, Certificate, Task, TaskSubmission, Module
# from .models import SCourse, SMaterial, Module, Staff


# @admin.register(User)
# class UserAdmin(DjangoUserAdmin):
#     fieldsets = DjangoUserAdmin.fieldsets + (
#         (None, {"fields": ("role",)}),
#     )
#     list_display = ("username", "email", "role", "is_staff", "is_superuser", "is_active")



# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'duration', 'price', 'Discount') 
#     search_fields = ('title',) 
#     list_filter = ('duration',)  
#     ordering = ('title',)
#     list_per_page = 20 

#     def image_tag(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="100" />'.format(obj.image.url))
#         return '-'
#     image_tag.short_description = 'Image'

# from django.contrib import admin
# from .models import Material

# @admin.register(Material)
# class MaterialAdmin(admin.ModelAdmin):
#     list_display = ('title', 'uploaded_at')
#     search_fields = ('title',)


# # @admin.register(SMaterial)
# # class SMaterialAdmin(admin.ModelAdmin):
# #     list_display = ('title', 'course')

# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ('student', 'course', 'completed')

# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course', 'due_date')

# @admin.register(TaskSubmission)
# class TaskSubmissionAdmin(admin.ModelAdmin):
#     list_display = ('task', 'student', 'submitted_at')


# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'phone', 'course')
#     list_filter = ('course',)
#     search_fields = ('user__username',)

# @admin.register(Staff)
# class StaffAdmin(admin.ModelAdmin):
#     list_display = ('user', 'phone', 'address', 'course')
#     search_fields = ('user__username', 'user__first_name', 'user__last_name', 'course__name')
#     list_filter = ('course',)




# class ModuleInline(admin.TabularInline):
#     model = Module
#     extra = 0

# @admin.register(SCourse)
# class SCourseAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'created_at')
#     inlines = [ModuleInline]
#     search_fields = ('name',)

# @admin.register(SMaterial)
# class SMaterialAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course')
#     list_filter = ('course',)
#     search_fields = ('title', 'course__name')
#     autocomplete_fields = ('course',)  # optional if many courses

# class ModuleInline(admin.TabularInline):
#     model = Module
#     extra = 1  # default empty module row

# @admin.register(Module)
# class ModuleAdmin(admin.ModelAdmin):
#     list_display = ('title', 'course', 'content_type', 'completion')



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User, Course, Student, Staff,
    Module, SMaterial, Certificate, Task, TaskSubmission
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (None, {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser", "is_active")

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'price')
    search_fields = ('title',)
    list_filter = ('duration',)
    inlines = [ModuleInline]
    ordering = ('title',)
    list_per_page = 20




@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'completion')


@admin.register(SMaterial)
class SMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    autocomplete_fields = ('course',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date')

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'student', 'submitted_at')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'course', 'course_duration', 'course_timing',
                    'location', 'occupation', 'company_college', 'end_goal')
    list_filter = ('course', 'course_duration', 'course_timing', 'location', 'occupation', 'end_goal')
    search_fields = ('user__username', 'company_college','phone','email')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'course')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'course__title')
    list_filter = ('course',)



# admin.py
from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.contrib.auth import get_user_model

from .models import Attendance, AttendancePeriod, Student

User = get_user_model()

class AttendanceInlineForm(forms.ModelForm):
    class Meta:
        model = Attendance
        exclude = ('marked_at',)
        widgets = {
            'status': forms.RadioSelect(choices=Attendance.STATUS_CHOICES),
        }

class AttendancePeriodForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Students', is_stacked=False),
        required=False
    )

    class Meta:
        model = AttendancePeriod
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@admin.register(AttendancePeriod)
class AttendancePeriodAdmin(admin.ModelAdmin):
    save_on_top = True   # ✅ THIS IS THE MAGIC LINE

    form = AttendancePeriodForm
    # filter_horizontal = ()
    list_display = ('__str__', 'start_date', 'end_date','view_attendance_link', 'student_count', 'created_at')
    list_filter = ('start_date', 'end_date')
    search_fields = ('students__user__username', 'students__user__first_name', 'students__user__last_name')
    # inlines = [AttendanceInline]
    readonly_fields = ('created_at', 'updated_at')

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Students'

    def save_model(self, request, obj, form, change):
        # limit created_by to staff
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        # regenerate rows AFTER saving (so M2M is ready)
        # obj.regenerate_attendance_rows()
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # ✅ regenerate AFTER M2M is saved
        form.instance.regenerate_attendance_rows()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Show only staff users for created_by
        if db_field.name == 'created_by':
            kwargs['queryset'] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Add a custom "Take Attendance" admin view/button
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('take-attendance/<int:period_id>/', self.admin_site.admin_view(self.take_attendance_view), name='attendance_take'),
        ]
        return my_urls + urls
    
    def view_attendance_link(self, obj):
        return format_html(
            '<a class="button" style="background-color:green; display:flex; text-align:center;" href="/admin/main/attendance/add/?period={}">Add Attendance</a>',
            obj.id
        )

    view_attendance_link.short_description = "Attendance"


    def take_attendance_view(self, request, period_id):
        period = self.get_object(request, period_id)
        if not period:
            self.message_user(request, "Attendance period not found", level='error')
            return redirect('..')

        # initial students list
        students_qs = period.students.all()

        if request.method == 'POST':
            # Expect: date, status, selected_students (list of student ids)
            selected_students = request.POST.getlist('students')
            date_str = request.POST.get('date')
            status = request.POST.get('status')
            note = request.POST.get('note', '')
            if date_str and status and selected_students:
                import datetime
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                for sid in selected_students:
                    st = Student.objects.filter(pk=int(sid)).first()
                    if not st:
                        continue
                    att, created = Attendance.objects.get_or_create(
                        period=period,
                        student=st,
                        date=date_obj,
                        defaults={'status': status, 'marked_by': request.user, 'note': note}
                    )
                    if not created:
                        att.status = status
                        att.note = note
                        att.marked_by = request.user
                        att.save()
                self.message_user(request, "Attendance saved for selected students.")
                # regenerate rows for safety
                period.regenerate_attendance_rows()
                # stay on the same page
                return redirect(request.path)

        # render admin template for attendance-taking
        context = dict(
            self.admin_site.each_context(request),
            period=period,
            students=students_qs,
            statuses=Attendance.STATUS_CHOICES,
        )
        return render(request, 'admin/take_attendance.html', context)


from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import Attendance, AttendancePeriod, Student

User = get_user_model()

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_by', 'marked_at', 'period')
    list_filter = ('status', 'date', 'period')
    search_fields = ('student__user__username', 'student__user__first_name', 'student__user__last_name', 'date')
    list_editable = ('status',)
    readonly_fields = ('marked_at',)

    def get_readonly_fields(self, request, obj=None):
        if request.GET.get('period'):
            return ('period',)
        return ()

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        period_id = request.GET.get('period')
        if period_id:
            initial['period'] = period_id
        return initial

    def has_add_permission(self, request):
        return bool(request.GET.get('period'))

    def save_model(self, request, obj, form, change):
        """
        Save Attendance with only one message.
        Updates existing records or creates new.
        """
        period_id = request.GET.get('period')
        if period_id:
            obj.period_id = int(period_id)
        obj.marked_by = request.user

        # Check for existing record
        attendance = Attendance.objects.filter(
            student=obj.student,
            date=obj.date,
            period=obj.period
        ).first()

        if attendance:
            attendance.status = obj.status
            attendance.note = obj.note
            attendance.marked_by = obj.marked_by
            attendance.save()
            messages.success(request, f"Attendance for {obj.student} on {obj.date} updated successfully.")
            
        else:
            obj.save()
            # messages.success(request, f"Attendance for {obj.student} on {obj.date} added successfully.")
            None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'student':
            period_id = request.GET.get('period')
            if period_id:
                try:
                    period = AttendancePeriod.objects.get(pk=period_id)
                    kwargs['queryset'] = period.students.all()
                except AttendancePeriod.DoesNotExist:
                    kwargs['queryset'] = Student.objects.none()
            else:
                kwargs['queryset'] = Student.objects.all()

        if db_field.name == 'marked_by':
            kwargs['queryset'] = User.objects.filter(is_staff=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)