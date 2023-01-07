from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.

def login(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')
    else:
        context_dict = {}
        return render(request, "user/login.html", context_dict)

