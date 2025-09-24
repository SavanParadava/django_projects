from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = 'autos'

urlpatterns = [
    path("",views.AutoListView.as_view(),name="auto-list"),
    path("main/create/",views.AutoCreateView.as_view(),name="auto-create"),
    path("main/<int:pk>/update/",views.AutoUpdateView.as_view(),name="auto-update"),
    path("main/<int:pk>/delete/",views.AutoDeleteView.as_view(),name="auto-delete"),

    path("lookup/",views.MakeListView.as_view(),name="make-list"),
    path("lookup/create/",views.MakeCreateView.as_view(),name="make-create"),
    path("lookup/<int:pk>/update/",views.MakeUpdateView.as_view(),name="make-update"),
    path("lookup/<int:pk>/delete/",views.MakeDeleteView.as_view(),name="make-delete"),
    # path('', TemplateView.as_view(template_name='home/main.html')),
]
