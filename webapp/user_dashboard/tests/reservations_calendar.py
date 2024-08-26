from more_itertools import first
from django.test import TestCase
from user_dashboard.models import ReservationsCalendar
from .fixtures import ReservationsCalendarFixtures
# Create your tests here.


class ReservationsCalendarTest(TestCase):
    fixtures_obj = ReservationsCalendarFixtures()

    def test_valid_unit_duration(self):
        "Unit duration must pass for values between 15 minutes up to 4 hours."
        calendar_info = zip(
            self.fixtures_obj.valid_unit_duration_values,
            self.fixtures_obj.valid_week_dates
        )
        for duration, week_date in calendar_info:
            o = ReservationsCalendar.objects.create(
                week_date=week_date,
                unit_duration=duration
            )
            o.full_clean()
            self.assertTrue(ReservationsCalendar.objects.get(pk=o.pk))

    def test_invalid_unit_duration(self):
        "Unit duration can't pass for values lower than 15 minutes or above 4 hours."
        calendar_info = zip(
            self.fixtures_obj.invalid_unit_duration_values,
            self.fixtures_obj.valid_week_dates
        )
        for duration, week_date in calendar_info:
            with self.assertRaises(ReservationsCalendar.UnitDurationError):
                o = ReservationsCalendar.objects.create(
                    week_date=week_date,
                    unit_duration=duration
                )
                o.full_clean()

    def test_calendar_doesnt_interleaves_with_others(self):
        "Multiple calendars have different valid times ranges (valid)."
        for date in self.fixtures_obj.valid_week_dates:
            o = ReservationsCalendar.objects.create(
                week_date=date,
                unit_duration=self.fixtures_obj.example_valid_unit_duration
            )
            o.full_clean()
            self.assertTrue(ReservationsCalendar.objects.get(pk=o.pk))

    def test_calendar_interleave_with_others(self):
        "Multiple calendars interleaves in dates with each other (invalid)."
        # insert first
        o = ReservationsCalendar.objects.create(
            week_date=first(self.fixtures_obj.invalid_week_dates),
            unit_duration=self.fixtures_obj.example_valid_unit_duration
        )
        o.full_clean()
        # check the rest
        for date in self.fixtures_obj.invalid_week_dates[1:]:
            with self.assertRaises(ReservationsCalendar.InterleaveError):
                o = ReservationsCalendar.objects.create(
                    week_date=date,
                    unit_duration=self.fixtures_obj.example_valid_unit_duration
                )
                o.full_clean()
