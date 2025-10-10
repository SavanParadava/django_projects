from django.urls import path, include
from .views import MyLoginView

app_name = "accounts"
urlpatterns = [
    path('login/', MyLoginView.as_view(),name='login'),
    path("",include("django.contrib.auth.urls"))
]