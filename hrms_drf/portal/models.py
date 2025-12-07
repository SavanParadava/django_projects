from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Position(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Employee(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    hire_date = models.DateField(auto_now_add=True)
    department = models.ForeignKey(Department,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True)
    position = models.ForeignKey(Position,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20,
                              choices=[
                                  ('present', 'Present'),
                                  ('absent', 'Absent'),
                                  ('leave', 'Leave'),
                              ],
                              null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'],
                                    name='unique_employee_date')
        ]

    def __str__(self):
        return f"{self.employee.first_name} - {self.date} - {self.status}"
