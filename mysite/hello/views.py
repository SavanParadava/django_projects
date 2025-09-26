from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def cookie_session_view(request):
    num_visits = request.session.get('num_visits', 0) + 1
    request.session['num_visits'] = num_visits 
    if num_visits > 4 : request.session['num_visits']=1
    resp = HttpResponse('view count='+str(num_visits))
    resp.set_cookie('dj4e_cookie', 'ae152933', max_age=1000)
    return resp
