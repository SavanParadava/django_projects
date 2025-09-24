from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from autos.models import Auto, Make

# Create your views here.
class AutoListView(LoginRequiredMixin,ListView):
    model = Auto

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["make_count"] = Make.objects.count()
        return context

class AutoCreateView(LoginRequiredMixin,CreateView):
    model = Auto
    fields = '__all__'
    success_url = reverse_lazy('autos:auto-list')

class AutoUpdateView(LoginRequiredMixin,UpdateView):
    model = Auto
    fields = '__all__'
    # template_name_suffix = "_update_form"
    success_url = reverse_lazy('autos:auto-list')

class AutoDeleteView(LoginRequiredMixin,DeleteView):
    model = Auto
    success_url = reverse_lazy('autos:auto-list')




class MakeListView(LoginRequiredMixin,ListView):
    model = Make

class MakeCreateView(LoginRequiredMixin,CreateView):
    model = Make
    fields = '__all__'
    success_url = reverse_lazy('autos:auto-list')

class MakeUpdateView(LoginRequiredMixin,UpdateView):
    model = Make
    fields = '__all__'
    # template_name_suffix = "_update_form"
    success_url = reverse_lazy('autos:auto-list')

class MakeDeleteView(LoginRequiredMixin,DeleteView):
    model = Make
    success_url = reverse_lazy('autos:auto-list')