from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class StringReverse(LoginRequiredMixin, View):
    def get(self,request):
        msg = request.session.get('msg',False)
        if msg: del(request.session['msg'])
        return render(request,"solo2/main.html",{'message':msg})
    def post(self,request):
        request.session['msg'] = request.POST.get('field2')[::-1] +" "+ request.POST.get('field1')[::-1]
        request.session['msg'] = request.session['msg'].title()
        return redirect(request.path)
