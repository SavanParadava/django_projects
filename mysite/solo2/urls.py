from django.urls import path
from . import views

app_name = 'solo2'

urlpatterns = [
    path("",views.StringReverse.as_view(),name='all'),
]