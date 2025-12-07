from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import LogoutView, UserViewSet, upload_user_photo
from rest_framework.routers import DefaultRouter

from portal.views import EmployeeViewSet, AttendanceViewSet, DepartmentViewSet, PositionViewSet

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user/me/upload_photo/',
         upload_user_photo,
         name='upload_user_photo'),
]

router = DefaultRouter()

router.register(r'api/department', DepartmentViewSet, basename='department')
router.register(r'api/position', PositionViewSet, basename='position')
router.register(r'api/employee', EmployeeViewSet, basename='employee')
router.register(r'api/user', UserViewSet, basename='user')
router.register(r'api/attendance', AttendanceViewSet, basename='attendance')

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += router.urls
