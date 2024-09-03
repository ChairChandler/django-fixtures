from datetime import date, time
from django.test import TestCase
from more_itertools import first
from user_dashboard.models import *
from user_dashboard.tests.fixtures import *


@use_fixture_namespace(ReservationsCalendarFixtures)
class ReservationsCalendarTest(TestCase):
    def tearDown(self):
        ReservationsCalendar.objects.all().delete()

    def test_valid_unit_duration(self, valid_unit_duration_values: list[time]):
        "Unit duration must pass for values between 15 minutes up to 4 hours."
        validator = validate_time(
            min_time=time(minute=15),
            max_time=time(hour=4)
        )

        for d in valid_unit_duration_values:
            validator(d)

    def test_invalid_unit_duration(
        self,
        invalid_unit_duration_values: list[time]
    ):
        '''
        Unit duration can't pass for values lower than 15 minutes or above
        4 hours.
        '''
        validator = validate_time(
            min_time=time(minute=15),
            max_time=time(hour=4)
        )

        for d in invalid_unit_duration_values:
            with self.assertRaises(ReservationsCalendar.TimeError):
                validator(d)

    def test_valid_lock_time(self, valid_lock_time_values: list[time]):
        "Lock time must pass for values between 30 minutes up to 1 day."
        validator = validate_time(
            min_time=time(minute=30),
            max_time=time(hour=23, minute=59, second=59)
        )

        for t in valid_lock_time_values:
            validator(t)

    def test_invalid_lock_time(self, invalid_lock_time_values: list[time]):
        "Lock time cannot pass for values below 30 minutes or above 1 day."
        validator = validate_time(
            min_time=time(hour=1),
            max_time=time(hour=23, minute=59, second=59)
        )

        for t in invalid_lock_time_values:
            with self.assertRaises(ReservationsCalendar.TimeError):
                validator(t)

    def test_calendar_doesnt_interleaves_with_others(
        self,
        valid_week_dates: list[date],
        valid_unit_duration_values: list[time]
    ):
        "Multiple calendars have different valid times ranges (valid)."
        duration = first(valid_unit_duration_values)

        for date in valid_week_dates:
            o = ReservationsCalendar.objects.create(
                week_date=date,
                unit_duration=duration
            )
            validate_calendar(o)

    def test_calendar_interleave_with_others(
        self,
        invalid_week_dates: list[date],
        valid_unit_duration_values: list[time]
    ):
        "Multiple calendars interleaves in dates with each other (invalid)."
        first_insert_date = first(invalid_week_dates)
        unit_duration = first(valid_unit_duration_values)
        another_insert_dates = invalid_week_dates[1:]

        # insert first
        o = ReservationsCalendar.objects.create(
            week_date=first_insert_date,
            unit_duration=unit_duration
        )
        # check the rest
        for date in another_insert_dates:
            with self.assertRaises(ReservationsCalendar.InterleaveError):
                o = ReservationsCalendar.objects.create(
                    week_date=date,
                    unit_duration=unit_duration
                )
                validate_calendar(o)
