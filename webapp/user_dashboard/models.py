from functools import wraps
from django.db import models
from django.forms import ValidationError
from accounts.models import User
import datetime

import uuid
# Create your models here.


def validate_time(min_time: datetime.time, max_time: datetime.time):
    "Check if time is in range <min_time; max_time>"
    @wraps(validate_time)
    def inner_validator(value: datetime.time):
        if value < min_time:
            raise ReservationsCalendar.TimeError(
                f'Time cannot be less than {min_time}'
            )
        if value > max_time:
            raise ReservationsCalendar.TimeError(
                f'Time cannot be more than {max_time}'
            )

    return inner_validator


def validate_calendar(value: 'ReservationsCalendar'):
    "Check if calendar doesn't interleave with another calendar."

    # create temporary field
    computed_field = models.ExpressionWrapper(
        expression=models.F('week_date') + datetime.timedelta(days=7),
        output_field=models.DateField()
    )

    # call methods on fields
    week = ReservationsCalendar.objects.annotate(week_date_end=computed_field)
    in_range = week.filter(
        ~models.Q(pk=value.pk),
        week_date__lte=value.week_date,
        week_date_end__gt=value.week_date,
    )
    if in_range.exists():
        raise ReservationsCalendar.InterleaveError(
            'Calendar interleave with the other calendar'
        )


class ReservationsCalendar(models.Model):
    "Week reservations calendar."
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    week_date = models.DateField(unique=True)
    unit_duration = models.TimeField(
        default=datetime.time(minute=45),
        validators=[
            validate_time(
                min_time=datetime.time(minute=15),
                max_time=datetime.time(hour=4)
            )]
    )
    # time right before reservation, that is locked, cannot change anything
    lock_time = models.TimeField(
        default=datetime.time(hour=5),
        validators=[
            validate_time(
                min_time=datetime.time(minute=30),
                max_time=datetime.time(hour=23, minute=59, second=59)
            )]
    )

    class TimeError(ValidationError):
        pass

    class InterleaveError(ValidationError):
        pass

    def clean(self):
        super().clean()
        validate_calendar(self)


def validate_reservation_dates(value: 'ReservationUnit'):
    "Check if start and stop date are valid."
    if value.date_start >= value.date_stop:
        raise ReservationUnit.InvalidDateError(
            'Invalid reservation dates'
        )


def validate_unique_reservation(value: 'ReservationUnit'):
    "Check if reservations don't interleaves with each other for the same calendar."
    interleave = ReservationUnit.objects.filter(
        ~models.Q(pk=value.pk),
        date_start__lt=value.date_stop,
        date_stop__gt=value.date_start,
        calendar=value.calendar,
    )
    if interleave.exists():
        raise ReservationUnit.CalendarReservationError(
            'Date interleave with the other dates'
        )


def validate_calendar_reservation(value: 'ReservationUnit'):
    '''
    Check if reservation unit belongs to the parent calendar week and has 
    preset calendar unit duration time.
    '''
    start_date = value.calendar.week_date
    end_date = value.calendar.week_date + datetime.timedelta(days=7)

    before_calendar_week = (value.date_start < start_date)
    after_calendar_week = (value.date_stop > end_date)

    if before_calendar_week or after_calendar_week:
        raise ReservationUnit.CalendarDateError(
            'Date does not belongs to the calendar week'
        )

    value_date_diff = (value.date_stop - value.date_start)

    if value_date_diff != value.calendar.unit_duration:
        raise ReservationUnit.CalendarDurationError(
            'Reservation has different duration time than preset in calendar'
        )


class ReservationUnit(models.Model):
    "Allows user to take up a reservation in a time-specific event."
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    # when
    date_start = models.DateTimeField()
    date_stop = models.DateTimeField()
    # calendar reference
    calendar = models.ForeignKey(
        ReservationsCalendar,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    # who
    participant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    # is accepted
    confirmed = models.BooleanField(default=False)

    class InvalidDateError(ValidationError):
        pass

    class CalendarReservationError(ValidationError):
        pass

    class CalendarDateError(ValidationError):
        pass

    class CalendarDurationError(ValidationError):
        pass

    def clean(self):
        super().clean()
        validate_reservation_dates(self)
        validate_unique_reservation(self)
        validate_calendar_reservation(self)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date_start', 'date_stop', 'calendar'],
                name='date_calendar_constraint'
            )
        ]
