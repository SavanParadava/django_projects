from django.urls import path
from .views import EmployeeDetailView ,EmployeeCreateView, AttendanceView, EmployeeDeleteView, EmployeePhotoUpdateView, PersonalAttendance

app_name = "portal"
urlpatterns = [
    path("employee/", EmployeeDetailView.as_view(),name='employee'),
    path("hr/", EmployeeCreateView.as_view(), name='hr'),
    path("hr/attendance/", AttendanceView.as_view(),name='attendance'),
    path("hr/delete/<int:pk>/", EmployeeDeleteView.as_view(),name='delete'),
    path("employee/uploadphoto/", EmployeePhotoUpdateView.as_view(),name='upload-photo'),
    path("employee/attendance/", PersonalAttendance.as_view(),name="personal-attendance")
]
