from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone

from accounts.views import EmployeeLoginRequiredMixin, HRLoginRequiredMixin
from .models import Employee, Attendance
from .forms import AttendanceFormSet, EmployeePhotoForm, EmployeeForm
from accounts.models import CustomUser
from .utils import generate_password
from datetime import timedelta

class EmployeeCreateView(HRLoginRequiredMixin,CreateView):
    # model = Employee
    form_class = EmployeeForm
    template_name = "portal/employee_form.html"
    success_url = reverse_lazy("portal:hr")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employee_list"] = Employee.objects.all()
        return context
    
    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        #  write password set code
        password=generate_password(8)
        user_created = CustomUser.objects.create_user(
                                                username=self.object.first_name + 
                                                    '_' + self.object.last_name + 
                                                str(Employee.objects.count()+1) ,
                                                password=password
                                                )
        self.object.user = user_created
        self.object.save()

        # send email here
        send_mail(
                "HRMS Django",
                f"Here is your employee username and password for hrms portal:\nusername:{self.object.user.username}\npassword:{password}",
                "info@hrms.com",
                [self.object.email],
                fail_silently=False,
            )
        del password

        messages.success(self.request, "Employee Created successfully! 🎉")
        return super().form_valid(form)

class EmployeeDeleteView(HRLoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'portal/employee_confirm_delete.html'
    success_url = reverse_lazy("portal:hr")

    context_object_name = 'employee' 

class EmployeeDetailView(EmployeeLoginRequiredMixin,DetailView):
    model = Employee
    context_object_name = 'employee' 

    def get_object(self, queryset=None):
        try:
            emp = Employee.objects.get(user=self.request.user)
        except Employee.DoesNotExist:
            logout(self.request)
            raise Http404("No Employee matches the given query.")
        return emp
    
class EmployeePhotoUpdateView(EmployeeLoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeePhotoForm
    template_name = "portal/employee_photo_form.html"
    success_url = reverse_lazy("portal:employee")

    def get_object(self):
        print("here get")
        return Employee.objects.get(user=self.request.user)

class AttendanceView(HRLoginRequiredMixin, View):
    template_name = "portal/attendance_update_form.html"

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        employees = Employee.objects.all()

        attendance_map = {
            att['employee_id']: att['status'] 
            for att in Attendance.objects.filter(date=today).values('employee_id', 'status')
        }

        initial_data = [
            {'employee': emp['id'], 'status': attendance_map.get(emp['id'], None)} 
            for emp in employees.values('id')
        ]

        formset = AttendanceFormSet(initial=initial_data)
        forms_with_employees = zip(formset, employees)

        return render(request, self.template_name, {
            "formset": formset,
            "forms_with_employees": forms_with_employees,
            "today_date": today
        })

    def post(self, request, *args, **kwargs):
        formset = AttendanceFormSet(request.POST)
        today = timezone.now().date()

        if formset.is_valid():
            for form in formset:
                employee = form.cleaned_data.get('employee')
                status = form.cleaned_data.get('status')

                if employee and status:
                    Attendance.objects.update_or_create(
                        employee=employee,
                        date = today,
                        defaults={'status': status},
                    )
            
            messages.success(request, "Attendance has been saved successfully! 🎉")
            return redirect('portal:hr')

        else:
            employees = Employee.objects.all()
            forms_with_employees = zip(formset, employees)

            return render(request, self.template_name, {
                "formset": formset,
                "forms_with_employees": forms_with_employees,
                "today_date": today
            })

class PersonalAttendance(EmployeeLoginRequiredMixin,DetailView):
    model = Attendance
    template_name = "portal/personal_attendance_detail.html"
    context_object_name = 'employee' 
    
    def get_object(self, queryset=None):
        try:
            emp = Employee.objects.get(user=self.request.user)
        except Employee.DoesNotExist:
            logout(self.request)
            raise Http404("No Employee matches the given query.")
        return emp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()

        records = Attendance.objects.filter(employee=employee)

        present_count = records.filter(status = 'present').count()
        absent_count = records.filter(status='absent').count()
        leave_count = records.filter(status='leave').count()
        total_days = records.count()

        if total_days > 0:
            attendance_percentage = (present_count / total_days) * 100
        else:
            attendance_percentage = 0

        context['present_count'] = present_count
        context['absent_count'] = absent_count
        context['leave_count'] = leave_count
        context['total_days'] = total_days
        context['attendance_percentage'] = attendance_percentage
        return context