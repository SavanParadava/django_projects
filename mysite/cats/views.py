from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from cats.models import Cat, Breed

# Create your views here.
class CatListView(LoginRequiredMixin,ListView):
    model = Cat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breed_count"] = Breed.objects.count()
        return context

class CatCreateView(LoginRequiredMixin,CreateView):
    model = Cat
    fields = '__all__'
    success_url = reverse_lazy('cats:cat-list')

class CatUpdateView(LoginRequiredMixin,UpdateView):
    model = Cat
    fields = '__all__'
    # template_name_suffix = "_update_form"
    success_url = reverse_lazy('cats:cat-list')

class CatDeleteView(LoginRequiredMixin,DeleteView):
    model = Cat
    success_url = reverse_lazy('cats:cat-list')




class BreedListView(LoginRequiredMixin,ListView):
    model = Breed

class BreedCreateView(LoginRequiredMixin,CreateView):
    model = Breed
    fields = '__all__'
    success_url = reverse_lazy('cats:cat-list')

class BreedUpdateView(LoginRequiredMixin,UpdateView):
    model = Breed
    fields = '__all__'
    # template_name_suffix = "_update_form"
    success_url = reverse_lazy('cats:cat-list')

class BreedDeleteView(LoginRequiredMixin,DeleteView):
    model = Breed
    success_url = reverse_lazy('cats:cat-list')