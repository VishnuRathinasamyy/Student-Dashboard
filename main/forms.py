# from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from .models import User

# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         # NOTE: role not exposed here — registration only creates 'student'
#         fields = ("username", "email", "password1", "password2")

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         user.role = "student"   # force student role on registration
#         if commit:
#             user.save()
#         return user

# class EditProfileForm(UserChangeForm):
#     password = None  # hide password field
#     class Meta:
#         model = User
#         fields = ("username", "email",)


# from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from .models import User, Student

# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)

#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2")

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data["email"]
#         user.role = "student"  # force student role
#         if commit:
#             user.save()
#             # Ensure Student object exists
#             Student.objects.get_or_create(user=user, defaults={'email': user.email})
#         return user

# class EditProfileForm(UserChangeForm):
#     password = None  # hide password field
#     class Meta:
#         model = User
#         fields = ("username", "email",)


from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        # Step 1: Create user
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = "student"  # must be set before saving
        if commit:
            user.save()  # triggers post_save signal to create Student
        return user


class EditProfileForm(UserChangeForm):
    password = None  # hide password field
    class Meta:
        model = User
        fields = ("username", "email",)



# from django import forms
# from django.contrib.admin.widgets import FilteredSelectMultiple
# from .models import Attendance, Student


# class AttendanceAdminForm(forms.ModelForm):
#     students = forms.ModelMultipleChoiceField(
#         queryset=Student.objects.all(),
#         widget=FilteredSelectMultiple("Students", is_stacked=False),
#         required=True
#     )

#     class Meta:
#         model = Attendance
#         fields = ('period', 'date', 'status', 'note')
