from django.urls import path, include
from django.views.generic import TemplateView
from . import views

app_name = 'cats'

urlpatterns = [
    path("",views.CatListView.as_view(),name="cat-list"),
    path("main/create/",views.CatCreateView.as_view(),name="cat-create"),
    path("main/<int:pk>/update/",views.CatUpdateView.as_view(),name="cat-update"),
    path("main/<int:pk>/delete/",views.CatDeleteView.as_view(),name="cat-delete"),

    path("lookup/",views.BreedListView.as_view(),name="breed-list"),
    path("lookup/create/",views.BreedCreateView.as_view(),name="breed-create"),
    path("lookup/<int:pk>/update/",views.BreedUpdateView.as_view(),name="breed-update"),
    path("lookup/<int:pk>/delete/",views.BreedDeleteView.as_view(),name="breed-delete"),
    # path('', TemplateView.as_view(template_name='home/main.html')),
]
