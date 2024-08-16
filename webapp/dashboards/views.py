from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from accounts.models import User

# Create your views here.


@login_required
def index(request):
    "Redirect user to his dashboard"

    user: User = request.user
    if user.is_superuser or user.is_staff:
        to = reverse('admin:index')
    else:
        to = reverse('user_dashboard:index')

    return HttpResponseRedirect(to)
