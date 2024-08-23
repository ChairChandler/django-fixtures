from datetime import datetime
from django.forms import ValidationError
from more_itertools import first
from django.test import TestCase
from user_dashboard.models import ReservationUnit, ReservationsCalendar


class ReservationUnitTest(TestCase):
    def test_valid_dates(
        self,
        start_date: datetime,
        example_valid_stop_date: datetime,
        example_calendar: ReservationsCalendar
    ):
        "If start date is before stop date, then create reservation."
        o = ReservationUnit.objects.create(
            date_start=start_date,
            date_stop=example_valid_stop_date,
            calendar=example_calendar
        )
        o.full_clean()
        self.assertTrue(ReservationUnit.objects.get(pk=o.pk))

    def test_invalid_dates(
        self,
        start_date: datetime,
        example_invalid_stop_date: datetime,
        example_calendar: ReservationsCalendar
    ):
        "If start date is after stop date, then throw exception."
        with self.assertRaises(ValidationError):
            o = ReservationUnit.objects.create(
                date_start=start_date,
                date_stop=example_invalid_stop_date,
                calendar=example_calendar
            )
            o.full_clean()

    def test_valid_unique_reservations(
        self,
        example_calendar: ReservationsCalendar,
        valid_reservation_dates: list[tuple]
    ):
        '''
        If reservations are assigned to the same calendar and not interleaves
        with each other, then pass.
        '''
        for (start, stop) in valid_reservation_dates:
            o = ReservationUnit.objects.create(
                date_start=start,
                date_stop=stop,
                calendar=example_calendar
            )
            o.full_clean()
            self.assertTrue(ReservationUnit.objects.get(pk=o.pk))

    def test_invalid_unique_reservations(
        self,
        example_calendar: ReservationsCalendar,
        invalid_reservation_dates: list[tuple]
    ):
        '''
        If reservations are assigned to the same calendar and interleaves
        with each other, then fail.
        '''
        # create first object
        start, stop = first(invalid_reservation_dates)
        ReservationUnit.objects.create(
            date_start=start,
            date_stop=stop,
            calendar=example_calendar
        )
        for (start, stop) in invalid_reservation_dates[1:]:
            with self.assertRaises(ValidationError):
                o = ReservationUnit.objects.create(
                    date_start=start,
                    date_stop=stop,
                    calendar=example_calendar
                )
                o.full_clean()

    def test_valid_dates_with_calendar_dates(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservations dates are in calendar week date, then pass. 
        '''
        pass

    def test_invalid_dates_with_calendar_dates(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservations dates are not in calendar week date, then fail.
        '''
        pass

    def test_valid_reservation_duration(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservation duration is different than calendar reservation duration, then fail.
        '''
        pass

    def test_invalid_reservation_duration(
        self,
        example_calendar: ReservationsCalendar
    ):
        '''
        If reservation duration is different than calendar reservation duration, then fail.
        '''
        pass
