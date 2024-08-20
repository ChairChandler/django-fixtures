from django.db import models
from django.forms import ValidationError
from accounts.models import User
import datetime

# Create your models here.


class ReservationUnit(models.Model):
    date_start = models.DateTimeField()
    date_stop = models.DateTimeField()
    # who
    participant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        parent_link=True,
        default=None
    )
    # is accepted
    confirmed = models.BooleanField(default=False)


def validate_time(min_time: datetime.time, max_time: datetime.time):
    "Check if time is in range <min_time; max_time>"
    def inner_validator(value: datetime.time):
        if value < min_time:
            raise ValidationError(f'Time cannot be less than {min_time}')
        if value > max_time:
            raise ValidationError(f'Time cannot be more than {max_time}')

    return inner_validator


def validate_calendar_reservation(value: ReservationUnit):
    '''
    Check if reservation unit belongs to the parent calendar week and has 
    preset calendar unit duration time.
    '''
    calendar: ReservationsCalendar = value.children.all().first()  # type: ignore

    start_date = calendar.week_date
    end_date = calendar.week_date + datetime.timedelta(days=7)

    if value.date_start < start_date or value.date_stop > end_date:
        raise ValidationError('Date doesnt belongs to the calendar week')

    if (value.date_stop - value.date_start) != calendar.unit_duration:
        raise ValidationError(
            'Reservation has different duration time than preset in calendar'
        )


def validate_unique_reservation(value: ReservationUnit):
    "Check if reservations don't interleaves wirth each other."
    interleave = ReservationUnit.objects.filter(
        date_start__lt__=value.date_stop,
        date_stop__gt__=value.date_start
    )
    if interleave.exists():
        raise ValidationError('Date interleave with the other dates')


def validate_calendar(value: 'ReservationsCalendar'):
    "Check if calendar doesn't interleave with another calendar."

    # create temporary field
    compuited_field = models.ExpressionWrapper(
        expression=models.F('week_date') + 7,
        output_field=models.DateField()
    )

    # call methods on fields
    week = ReservationsCalendar.objects.annotate(week_date_end=compuited_field)
    in_range = week.filter(
        week_date__lt__=value.week_date,
        week_date_end__gt__=value.week_date
    )
    if in_range.exists():
        raise ValidationError('Calendar interleave with the other calendar')


class ReservationsCalendar(models.Model):
    "Week reservations calendar."
    week_date = models.DateField(primary_key=True)
    unit_duration = models.TimeField(
        default=datetime.time(minute=45),
        validators=[
            validate_time(
                min_time=datetime.time(minute=15),
                max_time=datetime.time(hour=4)
            )]
    )
    reservation_units = models.ForeignKey(
        ReservationUnit,
        on_delete=models.CASCADE,
        parent_link=True,
        validators=[
            validate_calendar_reservation,
            validate_unique_reservation
        ]
    )

    def clean(self):
        validate_calendar(self)
        super().clean()
