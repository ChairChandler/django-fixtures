from functools import cached_property
from webapp.settings import TIME_ZONE
from datetime import datetime, time, timedelta, date
from more_itertools import first
from user_dashboard.models import ReservationsCalendar
import pytz

# I can't mix pytest fixtures with Django tests easily, I would like also
# to avoid Django fixtures files, so decided to use manual objects access
# to get fixtures workaround.

#
#
# ReservationsCalendar
#
#


TIME_ZONE_INFO = pytz.timezone(TIME_ZONE)


class ReservationsCalendarFixtures:
    @cached_property
    def _now(self):
        return datetime.date(datetime.now(tz=TIME_ZONE_INFO))

    @property
    def valid_week_dates(self) -> list[date]:
        return [
            self._now,
            self._now + timedelta(days=7),
            self._now + timedelta(days=14),
            self._now + timedelta(days=30),
            self._now + timedelta(days=60)
        ]

    @property
    def invalid_week_dates(self) -> list[date]:
        return [
            self._now,
            self._now + timedelta(days=2),
            self._now + timedelta(days=5),
            self._now + timedelta(days=9),
            self._now + timedelta(days=12)
        ]

    @property
    def valid_unit_duration_values(self) -> list[time]:
        return [
            time(minute=15, tzinfo=TIME_ZONE_INFO),
            time(minute=30, tzinfo=TIME_ZONE_INFO),
            time(hour=1, tzinfo=TIME_ZONE_INFO),
            time(hour=3, minute=59, tzinfo=TIME_ZONE_INFO),
            time(hour=4, tzinfo=TIME_ZONE_INFO)
        ]

    @property
    def invalid_unit_duration_values(self) -> list[time]:
        return [
            time(minute=2, tzinfo=TIME_ZONE_INFO),
            time(minute=14, tzinfo=TIME_ZONE_INFO),
            time(hour=4, minute=1, tzinfo=TIME_ZONE_INFO),
            time(hour=8, tzinfo=TIME_ZONE_INFO),
            time(hour=12, tzinfo=TIME_ZONE_INFO)
        ]

#
#
# ReservationUnit
#
#


class ReservationUnitFixtures:
    def __init__(self) -> None:
        self.calendar_fixtures = ReservationsCalendarFixtures()

    @cached_property
    def start_date(self) -> date:
        return datetime.now(tz=TIME_ZONE_INFO)

    @property
    def valid_stop_dates(self) -> list[date]:
        return [
            self.start_date + timedelta(minutes=1),
            self.start_date + timedelta(minutes=30),
            self.start_date + timedelta(hours=1),
            self.start_date + timedelta(days=1),
            self.start_date + timedelta(days=2)
        ]

    @property
    def invalid_stop_dates(self) -> list[date]:
        return [
            self.start_date - timedelta(minutes=1),
            self.start_date - timedelta(minutes=30),
            self.start_date - timedelta(hours=1),
            self.start_date - timedelta(days=1),
            self.start_date - timedelta(days=2)
        ]

    @cached_property
    def example_calendar(self) -> ReservationsCalendar:
        example_unit_duration = first(
            self.calendar_fixtures.valid_unit_duration_values
        )
        return ReservationsCalendar.objects.create(
            week_date=self.start_date,
            unit_duration=example_unit_duration
        )

    @property
    def valid_reservation_dates(self) -> list[tuple[date, date]]:
        '''
        [r1, r2, r3]

        r = (start_date, stop_date)

        r1 < r2 < r3
        '''
        diff = timedelta(hours=1)
        return [
            (self.start_date, self.start_date + diff),
            (self.start_date + diff, self.start_date + 2*diff),
            (self.start_date + 10*diff, self.start_date + 11*diff)
        ]

    @property
    def invalid_reservation_dates(self) -> list[tuple[date, date]]:
        '''
        [r1, r2, r3]

        r = (start_date, stop_date)

        r[i+1].start_date < r[i].stop_date
        '''
        diff = timedelta(hours=1)
        return [
            (self.start_date, self.start_date + diff),
            (self.start_date + 0.5*diff, self.start_date + 2*diff),
            (self.start_date + 1.5*diff, self.start_date + 5*diff)
        ]

    @property
    def invalid_dates_with_calendar_dates(self) -> list[tuple[date, date]]:
        "returns [(start_reservation, stop_reservation)]"
        date = self.example_calendar.week_date
        return [
            (date - timedelta(days=5), date - timedelta(days=3)),
            (date + timedelta(days=14), date + timedelta(15))
        ]

    @property
    def invalid_reservation_duration(self) -> timedelta:
        "different duration than value in calendar"
        calendar = self.example_calendar
        time_val = self.calendar_fixtures.valid_unit_duration_values

        # find unit duration different than duration in calendar
        duration = first(
            filter(lambda v: v != calendar.unit_duration, time_val)
        )
        # convert time to difference
        diff = timedelta(minutes=duration.minute, hours=duration.hour)

        return diff
