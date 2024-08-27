import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpRequest
from django.shortcuts import redirect, render
import django.contrib.messages as messages
from accounts.models import User
from .models import ReservationUnit

from webapp.settings import TIME_ZONE
import pytz

# Create your views here.


@login_required
def redirect_to_current_calendar(request: HttpRequest):
    return redirect('')


@login_required
def show_calendar(request: HttpRequest, calendar_id: str):
    return render(request, 'user_dashboard/calendar.html', {})


@login_required
@require_POST
def join_reservation(request: HttpRequest, reservation_id: str):
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
        except:
            messages.error(request, 'Cannot change participant')

    return redirect(request.GET.get('next'))


@login_required
@require_POST
def cancel_reservation(request: HttpRequest, reservation_id: str):
    reservation = ReservationUnit.objects.get(pk=reservation_id)
    user: User = request.user  # type: ignore

    if reservation.participant != user:
        messages.error(
            request,
            'User cannot change reservation of another user.'
        )
    else:
        TIME_ZONE_INFO = pytz.timezone(TIME_ZONE)

        now = datetime.datetime.now(TIME_ZONE_INFO)
        diff = now - reservation.date_start

        lk = reservation.calendar.lock_time
        lk_delta = datetime.timedelta(
            hours=lk.hour,
            minutes=lk.minute,
            seconds=lk.second
        )

        if diff < lk_delta:
            messages.error(
                request,
                f'Cannot cancel reservation before {reservation.calendar.lock_time} time.'
            )
        else:
            try:
                reservation.participant = None
                reservation.save()
                messages.success(request, 'Successfully cancelled')
            except:
                messages.error(request, 'Cannot cancell reservation')

    return redirect(request.GET.get('next'))
