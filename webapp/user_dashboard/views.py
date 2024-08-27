from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpRequest
from django.shortcuts import redirect, render
import django.contrib.messages as messages
from webapp.accounts.models import User
from .models import ReservationUnit

# Create your views here.


@login_required
def redirect_to_current_calendar(request: HttpRequest):
    return redirect('')


@login_required
def show_calendar(request: HttpRequest, calendar_id: str):
    return render(request, 'user_dashboard/calendar.html', {})


@login_required
@require_POST
def check_reservation_participant(request: HttpRequest, reservation_id: str):
    reservation = ReservationUnit.objects.get(pk=reservation_id)
    if reservation.participant is not None:
        messages.error(
            request,
            'Cannot change participant if another already set.'
        )
    else:
        try:
            user: User = request.user  # type: ignore
            reservation.participant = user
            reservation.save()
            messages.success(request, 'Successfully joined')
        except Exception:
            messages.error(request, 'Cannot change participant')

    return redirect(request.GET.get('next'))
