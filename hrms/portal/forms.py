from django import forms
from .models import Attendance, Employee

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'status']
        widgets = {
            'employee': forms.HiddenInput(),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

AttendanceFormSet = forms.formset_factory(AttendanceForm, extra=0)

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'department', 'position']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g., john.doe@example.com'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
        }

class EmployeePhotoForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['photo']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control'})
        }