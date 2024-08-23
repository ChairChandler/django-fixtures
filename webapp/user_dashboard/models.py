from django.db import models
from django.forms import ValidationError
from accounts.models import User
import datetime
from webapp.user_dashboard.models import ReservationUnit

# Create your models here.


def validate_time(min_time: datetime.time, max_time: datetime.time):
    "Check if time is in range <min_time; max_time>"
    def inner_validator(value: datetime.time):
        if value < min_time:
            raise ValidationError(f'Time cannot be less than {min_time}')
        if value > max_time:
            raise ValidationError(f'Time cannot be more than {max_time}')

    return inner_validator


def validate_calendar(value: 'ReservationsCalendar'):
    "Check if calendar doesn't interleave with another calendar."

    # create temporary field
    computed_field = models.ExpressionWrapper(
        expression=models.F('week_date') + 7,
        output_field=models.DateField()
    )

    # call methods on fields
    week = ReservationsCalendar.objects.annotate(week_date_end=computed_field)
    in_range = week.filter(
        week_date__lt__=value.week_date,
        week_date_end__gt__=value.week_date
    )
    if in_range.exists():
        raise ValidationError('Calendar interleave with the other calendar')


class ReservationsCalendar(models.Model):
    "Week reservations calendar."
    uuid = models.UUIDField(primary_key=True)
    week_date = models.DateField(unique=True)
    unit_duration = models.TimeField(
        default=datetime.time(minute=45),
        validators=[
            validate_time(
                min_time=datetime.time(minute=15),
                max_time=datetime.time(hour=4)
            )]
    )

    def clean(self):
        super().clean()
        validate_calendar(self)


def validate_reservation_dates(value: ReservationUnit):
    "Check if start and stop date are valid."
    if value.date_start >= value.date_stop:
        raise ValidationError('Invalid reservation dates')


def validate_unique_reservation(value: ReservationUnit):
    "Check if reservations don't interleaves wirth each other for the same calendar."
    interleave = ReservationUnit.objects.filter(
        date_start__lt__=value.date_stop,
        date_stop__gt__=value.date_start,
        calendar=value.calendar
    )
    if interleave.exists():
        raise ValidationError('Date interleave with the other dates')


def validate_calendar_reservation(value: ReservationUnit):
    '''
    Check if reservation unit belongs to the parent calendar week and has 
    preset calendar unit duration time.
    '''
    start_date = value.calendar.week_date
    end_date = value.calendar.week_date + datetime.timedelta(days=7)

    if value.date_start < start_date or value.date_stop > end_date:
        raise ValidationError('Date does not belongs to the calendar week')

    if (value.date_stop - value.date_start) != value.calendar.unit_duration:
        raise ValidationError(
            'Reservation has different duration time than preset in calendar'
        )


class ReservationUnit(models.Model):
    "Allows user to take up a reservation in a time-specific event."
    uuid = models.UUIDField(primary_key=True)
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
