from datetime import date, timedelta
from django.test import TestCase
from more_itertools import first
from user_dashboard.models import *
from user_dashboard.tests.fixtures import *


@use_fixture_namespace(ReservationUnitFixtures)
class ReservationUnitTest(TestCase):
    def tearDown(self):
        ReservationUnit.objects.all().delete()
        ReservationsCalendar.objects.all().delete()

    def test_valid_dates(
        self,
        start_date: date,
        valid_stop_dates: list[date],
        example_calendar: ReservationsCalendar
    ):
        "If start date is before stop date, then create reservation."
        date_stop = first(valid_stop_dates)

        o = ReservationUnit.objects.create(
            date_start=start_date,
            date_stop=date_stop,
            calendar=example_calendar
        )
        validate_reservation_dates(o)

    def test_invalid_dates(
        self,
        start_date: date,
        invalid_stop_dates: list[date],
        example_calendar: ReservationsCalendar
    ):
        "If start date is after stop date, then throw exception."
        date_stop = first(invalid_stop_dates)

        with self.assertRaises(ReservationUnit.InvalidDateError):
            o = ReservationUnit.objects.create(
                date_start=start_date,
                date_stop=date_stop,
                calendar=example_calendar
            )
            validate_reservation_dates(o)

    def test_valid_unique_reservations(
        self,
        valid_reservation_dates: list[tuple[date, date]],
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservations are assigned to the same calendar and not interleaves
        with each other, then pass.
        '''
        for start, stop in valid_reservation_dates:
            o = ReservationUnit.objects.create(
                date_start=start,
                date_stop=stop,
                calendar=example_calendar
            )
            validate_unique_reservation(o)

    def test_invalid_unique_reservations(
        self,
        invalid_reservation_dates: list[tuple[date, date]],
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservations are assigned to the same calendar and interleaves
        with each other, then fail.
        '''
        (start, stop) = first(invalid_reservation_dates)
        another_dates = invalid_reservation_dates[1:]

        # create first object
        ReservationUnit.objects.create(
            date_start=start,
            date_stop=stop,
            calendar=example_calendar
        )
        for start, stop in another_dates:
            with self.assertRaises(ReservationUnit.CalendarReservationError):
                o = ReservationUnit.objects.create(
                    date_start=start,
                    date_stop=stop,
                    calendar=example_calendar
                )
                validate_unique_reservation(o)

    def test_invalid_dates_with_calendar_dates(
        self,
        example_calendar: ReservationsCalendar,
        invalid_dates_with_calendar_dates: list[tuple[date, date]]
    ):
        '''
        If reservations dates are not in calendar week date, then fail.
        '''
        for start, stop in invalid_dates_with_calendar_dates:
            with self.assertRaises(ReservationUnit.CalendarDateError):
                o = ReservationUnit.objects.create(
                    date_start=start,
                    date_stop=stop,
                    calendar=example_calendar
                )
                validate_calendar_reservation(o)

    def test_invalid_reservation_duration(
        self,
        example_calendar: ReservationsCalendar,
        invalid_reservation_duration: timedelta
    ):
        '''
        If reservation duration is different than calendar reservation 
        duration, then fail.
        '''

        with self.assertRaises(ReservationUnit.CalendarDurationError):
            o = ReservationUnit.objects.create(
                date_start=example_calendar.week_date,
                date_stop=example_calendar.week_date + invalid_reservation_duration,
                calendar=example_calendar
            )
            validate_calendar_reservation(o)
