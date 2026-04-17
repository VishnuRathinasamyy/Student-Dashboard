from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import add_student

urlpatterns = [
    path('', views.home, name="home"),
    path('course-overview/', views.course_overview, name='course_overview'),
    path("certificates/", views.certificates, name="certificates"),
    path('student-panel/', views.student_panel, name='student_panel'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # profile / dashboards
    path("profile/", views.profile, name="profile"),
    path("panel/admin/", views.admin_panel, name="admin_panel"),
    path("panel/staff/", views.staff_panel, name="staff_panel"),

    # password reset
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"),
        name="password_reset"),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done"),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name="password_reset_confirm"),
    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete"),
    path('activate/<uidb64>/<token>/', views.activate_user, name="activate"),
    path("password-change/",
     auth_views.PasswordChangeView.as_view(template_name="password_change.html"),
     name="password_change"),
    path("password-change/done/",
     auth_views.PasswordChangeDoneView.as_view(template_name="password_change_done.html"),
     name="password_change_done"),

    path('api/add-student/', add_student, name='add-student'),
    path('webhook/add-student/', views.add_student, name='add_student'),
    path('courses/', views.course_list, name='course_list'),
    path('s-materials/', views.materials_page, name='s_materials'),
    path('s-materials/preview/<int:pk>/', views.material_preview, name='material_preview'),
    path('submit/', views.submit_task, name='submit_task'),
    path("module-preview/<int:pk>/", views.module_preview, name="module_preview"),
    path("student/<int:id>/photo/", views.student_photo_edit, name="student_photo_edit"),
    path('student/<int:student_id>/attendance/', views.student_attendance_view, name='student_attendance_admin_view'),
    path('my-attendance/', views.student_attendance_view, name='student_attendance'),  # for student themselves

]











