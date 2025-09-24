from django.urls import path, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("",views.AutoListView.as_view()),
    path("/lookup",views.MakeListView.as_view()),
    # path('', TemplateView.as_view(template_name='home/main.html')),
    path("/lookup/create",views.MakeCreateView.as_view()),
    path("/lookup/<int:make_id>/update",views.MakeUpdateView.as_view()),
    path("/lookup/<int:make_id>/delete",views.MakeDeleteView.as_view()),
    path("/main/create",views.AutoCreateView.as_view()),
    path("/main/<int:auto_id>/update",views.AutoUpdateView.as_view()),
    path("/main/<int:auto_id>/delete",views.AutoDeleteView.as_view()),
]
