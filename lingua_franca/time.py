#
# Copyright 2018 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from dateutil.tz import gettz, tzlocal
from lingua_franca.lang import get_primary_lang_code
from datetime import timedelta, datetime, date
from lingua_franca.lang.parse_common import DateResolution, Season
from lingua_franca.lang.common_data_en import _MONTH_EN, _WEEKDAY_EN, \
    _MONTH_SHORT_EN, _WEEKDAY_SHORT_EN
from lingua_franca.location import Hemisphere
# used to calculate durations
DAYS_IN_1_YEAR = 365.2425
DAYS_IN_1_MONTH = 30.42


def default_timezone():
    """ Get the default timezone

    default system value

    Returns:
        (datetime.tzinfo): Definition of the default timezone
    """
    # Just go with system default timezone
    return tzlocal()


def now_utc():
    """ Retrieve the current time in UTC

    Returns:
        (datetime): The current time in Universal Time, aka GMT
    """
    return to_utc(datetime.utcnow())


def now_local(tz=None):
    """ Retrieve the current time

    Args:
        tz (datetime.tzinfo, optional): Timezone, default to user's settings

    Returns:
        (datetime): The current time
    """
    if not tz:
        tz = default_timezone()
    return datetime.now(tz)


def to_utc(dt):
    """ Convert a datetime with timezone info to a UTC datetime

    Args:
        dt (datetime): A datetime (presumably in some local zone)
    Returns:
        (datetime): time converted to UTC
    """
    tzUTC = gettz("UTC")
    if dt.tzinfo:
        return dt.astimezone(tzUTC)
    else:
        return dt.replace(tzinfo=gettz("UTC")).astimezone(tzUTC)


def to_local(dt):
    """ Convert a datetime to the user's local timezone

    Args:
        dt (datetime): A datetime (if no timezone, defaults to UTC)
    Returns:
        (datetime): time converted to the local timezone
    """
    tz = default_timezone()
    if dt.tzinfo:
        return dt.astimezone(tz)
    else:
        return dt.replace(tzinfo=gettz("UTC")).astimezone(tz)


def int_to_month(month, lang=None):
    lang_code = get_primary_lang_code(lang)
    if lang_code.startswith("en"):
        return _MONTH_EN[month]
    return str(month)


def int_to_weekday(weekday, lang=None):
    lang_code = get_primary_lang_code(lang)
    if lang_code.startswith("en"):
        return _WEEKDAY_EN[weekday]
    return str(weekday)


def month_to_int(month, lang=None):
    if isinstance(month, int) or isinstance(month, float):
        return int(month)
    lang_code = get_primary_lang_code(lang)
    inv_map = {}
    if lang_code.startswith("en"):
        inv_map = {v: k for k, v in _MONTH_SHORT_EN.items()}
    for short in inv_map:
        if month.startswith(short):
            return inv_map[short]
    return None


def weekday_to_int(weekday, lang=None):
    if isinstance(weekday, int) or isinstance(weekday, float):
        return int(weekday)
    lang_code = get_primary_lang_code(lang)
    inv_map = {}
    if lang_code.startswith("en"):
        inv_map = {v: k for k, v in _WEEKDAY_SHORT_EN.items()}

    for short in inv_map:
        if weekday.startswith(short):
            return inv_map[short]
    return None


def get_week_range(ref_date):
    start = ref_date - timedelta(days=ref_date.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_weekend_range(ref_date):
    if ref_date.weekday() < 5:
        start, end = get_week_range(ref_date)
        start = start + timedelta(days=5)
    elif ref_date.weekday() == 5:
        start = ref_date
    elif ref_date.weekday() == 6:
        start = ref_date - timedelta(days=1)
    return start, start + timedelta(days=1)


def get_month_range(ref_date):
    start = ref_date.replace(day=1)
    end = ref_date.replace(day=1, month=ref_date.month + 1) - timedelta(days=1)
    return start, end


def get_year_range(ref_date):
    start = ref_date.replace(day=1, month=1)
    end = ref_date.replace(day=31, month=12)
    return start, end


def get_decade_range(ref_date):
    start = date(day=1, month=1, year=(ref_date.year // 10)*10)
    end = date(day=31, month=12, year=start.year + 9)
    return start, end


def get_century_range(ref_date):
    start = date(day=1, month=1, year=(ref_date.year // 100) * 100)
    end = date(day=31, month=12, year=start.year + 99)
    return start, end


def get_millennium_range(ref_date):
    start = date(day=1, month=1, year=(ref_date.year // 1000) * 1000)
    end = date(day=31, month=12, year=start.year + 999)
    return start, end


def get_ordinal(ordinal, ref_date=None,
                resolution=DateResolution.DAY_OF_MONTH):
    ordinal = int(ordinal)
    ref_date = ref_date or now_local()
    if isinstance(ref_date, datetime):
        ref_date = ref_date.date()

    _decade = (ref_date.year // 10) * 10 or 1
    _century = (ref_date.year // 100) * 100 or 1
    _mil = (ref_date.year // 1000) * 1000 or 1

    if resolution == DateResolution.DAY:
        if ordinal < 0:
            raise OverflowError("The last day of existence can not be "
                                "represented")
        ordinal -= 1
        return date(year=1, day=1, month=1) + timedelta(days=ordinal)
    if resolution == DateResolution.DAY_OF_MONTH:
        if ordinal == -1:
            # last day
            if ref_date.month + 1 == 13:
                return ref_date.replace(day=31, month=12)
            return ref_date.replace(month=ref_date.month + 1, day=1) - \
                   timedelta(days=1)
        return ref_date.replace(day=ordinal)
    if resolution == DateResolution.DAY_OF_YEAR:
        if ordinal == -1:
            # last day
            return date(year=ref_date.year, day=31, month=12)
        ordinal -= 1
        return date(year=ref_date.year, day=1, month=1) + \
               timedelta(days=ordinal)
    if resolution == DateResolution.DAY_OF_DECADE:
        if ordinal == -1:
            # last day
            if _decade + 10 == 10000:
                return date(year=9999, day=31, month=12)
            return date(year=_decade + 10, day=1, month=1) - timedelta(1)
        ordinal -= 1
        return date(year=_decade, day=1, month=1) + timedelta(days=ordinal)

    if resolution == DateResolution.DAY_OF_CENTURY:
        if ordinal == -1:
            # last day
            if _century + 100 == 10000:
                return date(year=9999, day=31, month=12)
            return date(year=_century + 100, day=1, month=1) - timedelta(1)

        return datetime(year=_century, day=1, month=1).date() + timedelta(days=ordinal - 1)

    if resolution == DateResolution.DAY_OF_MILLENIUM:
        if ordinal == -1:
            # last day
            if _mil + 1000 == 10000:
                return date(year=9999, day=31, month=12)
            return date(year=_mil + 1000, day=1, month=1) - timedelta(1)
        return date(year=_mil, day=1, month=1) + timedelta(days=ordinal - 1)

    if resolution == DateResolution.WEEK:
        if ordinal < 0:
            raise OverflowError("The last week of existence can not be "
                                "represented")
        return date(year=1, day=1, month=1) + timedelta(weeks=ordinal)
    if resolution == DateResolution.WEEK_OF_MONTH:
        if ordinal == -1:
            _start, _end = get_week_range(ref_date.replace(day=28))
            return _start
        _start, _end = get_week_range(
            ref_date.replace(day=1) + timedelta(weeks=ordinal - 1))
        return _start
    if resolution == DateResolution.WEEK_OF_YEAR:
        if ordinal == -1:
            _start, _end = get_week_range(ref_date.replace(day=31, month=12))
            return _start
        return ref_date.replace(day=1, month=1) + timedelta(weeks=ordinal - 1)

    if resolution == DateResolution.WEEK_OF_DECADE:
        if ordinal == -1:
            _start, _end = get_week_range(date(day=31, month=12,
                                               year=_decade + 9))
            return _start
        if ordinal == 1:
            return date(day=1, month=1, year=_decade)
        ordinal -= 1
        return date(day=1, month=1, year=_decade) + timedelta(weeks=ordinal)
    if resolution == DateResolution.WEEK_OF_CENTURY:
        if ordinal == -1:
            _start, _end = get_week_range(date(day=31, month=12,
                                               year=_century + 99))
            return _start
        if ordinal == 1:
            return date(day=1, month=1, year=_century)
        ordinal -= 1
        return date(day=1, month=1, year=_century) + timedelta(weeks=ordinal)
    if resolution == DateResolution.WEEK_OF_MILLENIUM:
        if ordinal == -1:
            _start, _end = get_week_range(date(day=31, month=12,
                                               year=_mil + 999))
            return _start
        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        ordinal -= 1
        return date(day=1, month=1, year=_mil) + timedelta(weeks=ordinal)

    if resolution == DateResolution.MONTH:
        if ordinal < 0:
            raise OverflowError("The last month of existence can not be "
                                "represented")
        return date(year=1, day=1, month=1) + timedelta(weeks=ordinal * 4)
    if resolution == DateResolution.MONTH_OF_YEAR:
        if ordinal == -1:
            return ref_date.replace(month=12, day=1)
        return ref_date.replace(month=ordinal, day=1)
    if resolution == DateResolution.MONTH_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 99, day=1, month=12)
        _date = ref_date.replace(month=1, day=1, year=_century)
        _date += ordinal * timedelta(weeks=4)
        return _date - timedelta(days=1)
    if resolution == DateResolution.MONTH_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=1, month=12)
        _date = ref_date.replace(month=1, day=1, year=_decade)
        _date += ordinal * timedelta(weeks=4)
        return _date - timedelta(days=1)
    if resolution == DateResolution.MONTH_OF_MILLENIUM:
        if ordinal == -1:
            return date(year=_mil + 999, day=1, month=12)
        _date = ref_date.replace(month=1, day=1, year=_mil)
        _date += ordinal * timedelta(weeks=4)
        return _date - timedelta(days=1)

    if ordinal == 0:
        # NOTE: no year 0
        return date(year=1, day=1, month=1)

    if resolution == DateResolution.YEAR:
        if ordinal == -1:
            raise OverflowError("The last year of existence can not be "
                                "represented")
        return date(year=ordinal, day=1, month=1)
    if resolution == DateResolution.YEAR_OF_DECADE:
        if ordinal == -1:
            return date(year=_decade + 9, day=31, month=12)
        assert 0 < ordinal < 10
        return date(year=_decade + ordinal, day=1, month=1)
    if resolution == DateResolution.YEAR_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century - 1, day=31, month=12)
        return date(year=_century + ordinal, day=1, month=1)
    if resolution == DateResolution.YEAR_OF_MILLENIUM:
        if ordinal == -1:
            return date(year=_mil - 1, day=31, month=12)
        return date(year=_mil + ordinal, day=1, month=1)
    if resolution == DateResolution.DECADE:
        if ordinal == -1:
            raise OverflowError("The last decade of existence can not be "
                                "represented")
        if ordinal == 1:
            return date(day=1, month=1, year=1)
        ordinal -= 1
        return date(year=ordinal * 10, day=1, month=1)
    if resolution == DateResolution.DECADE_OF_CENTURY:
        if ordinal == -1:
            return date(year=_century + 90, day=1, month=1)

        assert 0 < ordinal < 10

        if ordinal == 1:
            return date(day=1, month=1, year=_century)
        ordinal -= 1

        return date(year=_century + ordinal * 10, day=1, month=1)
    if resolution == DateResolution.DECADE_OF_MILLENIUM:
        if ordinal == -1:
            return date(year=_mil + 990, day=1, month=1)

        assert 0 < ordinal < 1000

        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        ordinal -= 1
        return date(year=_mil + ordinal * 10,  day=1, month=1)
    if resolution == DateResolution.CENTURY:
        if ordinal == -1:
            raise OverflowError("The last century of existence can not be "
                                "represented")
        return date(year=ordinal * 100, day=1, month=1)
    if resolution == DateResolution.CENTURY_OF_MILLENIUM:
        if ordinal == -1:
            return date(year=_mil + 900, day=1, month=1)

        assert 0 < ordinal < 100

        if ordinal == 1:
            return date(day=1, month=1, year=_mil)
        ordinal -= 1
        return date(year=_mil + ordinal * 100,  day=1, month=1)
    if resolution == DateResolution.MILLENNIUM:
        if ordinal < 0:
            raise OverflowError("The last millennium of existence can not be "
                                "represented")
        if ordinal == 1:
            return date(day=1, month=1, year=1)
        return date(year=ordinal * 1000, day=1, month=1)
    raise ValueError


def date_to_season(ref_date=None, hemisphere=Hemisphere.NORTH):
    ref_date = ref_date or now_local().date()

    if hemisphere == Hemisphere.NORTH:
        fall = (
            date(day=1, month=9, year=ref_date.year),
            date(day=30, month=11, year=ref_date.year)
        )
        spring = (
            date(day=1, month=3, year=ref_date.year),
            date(day=31, month=5, year=ref_date.year)
        )
        summer = (
            date(day=1, month=6, year=ref_date.year),
            date(day=31, month=8, year=ref_date.year)
        )

        if fall[0] <= ref_date < fall[1]:
            return Season.FALL
        if summer[0] <= ref_date < summer[1]:
            return Season.SUMMER
        if spring[0] <= ref_date < spring[1]:
            return Season.SPRING
        return Season.WINTER

    else:
        spring = (
            date(day=1, month=9, year=ref_date.year),
            date(day=30, month=11, year=ref_date.year)
        )
        fall = (
            date(day=1, month=3, year=ref_date.year),
            date(day=31, month=5, year=ref_date.year)
        )
        winter = (
            date(day=1, month=6, year=ref_date.year),
            date(day=31, month=8, year=ref_date.year)
        )

        if fall[0] <= ref_date < fall[1]:
            return Season.FALL
        if winter[0] <= ref_date < winter[1]:
            return Season.WINTER
        if spring[0] <= ref_date < spring[1]:
            return Season.SPRING
        return Season.SUMMER


def season_to_date(season, year=None, hemisphere=Hemisphere.NORTH):
    if year is None:
        year = now_local().year
    elif not isinstance(year, int):
        year = year.year

    if hemisphere == Hemisphere.NORTH:
        if season == Season.SPRING:
            return date(day=1, month=3, year=year)
        elif season == Season.FALL:
            return date(day=1, month=9, year=year)
        elif season == Season.WINTER:
            return date(day=1, month=12, year=year)
        elif season == Season.SUMMER:
            return date(day=1, month=6, year=year)
    else:
        if season == Season.SPRING:
            return date(day=1, month=9, year=year)
        elif season == Season.FALL:
            return date(day=1, month=3, year=year)
        elif season == Season.WINTER:
            return date(day=1, month=6, year=year)
        elif season == Season.SUMMER:
            return date(day=1, month=12, year=year)
    raise ValueError("Unknown Season")


def next_season_date(season, ref_date=None, hemisphere=Hemisphere.NORTH):
    ref_date = ref_date or now_local().date()
    start_day = season_to_date(season, ref_date, hemisphere) \
        .timetuple().tm_yday
    # get the current day of the year
    doy = ref_date.timetuple().tm_yday

    if doy <= start_day:
        # season is this year
        return season_to_date(season, ref_date, hemisphere)
    else:
        # season is next year
        ref_date = ref_date.replace(year=ref_date.year + 1)
        return season_to_date(season, ref_date, hemisphere)


def last_season_date(season, ref_date=None, hemisphere=Hemisphere.NORTH):
    ref_date = ref_date or now_local().date()

    start_day = season_to_date(season, ref_date, hemisphere)\
        .timetuple().tm_yday
    # get the current day of the year
    doy = ref_date.timetuple().tm_yday

    if doy <= start_day:
        # season is previous year
        ref_date = ref_date.replace(year=ref_date.year - 1)
        return season_to_date(season, ref_date, hemisphere)
    else:
        # season is this year
        return season_to_date(season, ref_date, hemisphere)


def get_season_range(ref_date=None, hemisphere=Hemisphere.NORTH):
    ref_date = ref_date or now_local().date()
    if hemisphere == Hemisphere.NORTH:
        fall = (
            date(day=1, month=9, year=ref_date.year),
            date(day=30, month=11, year=ref_date.year)
        )
        spring = (
            date(day=1, month=3, year=ref_date.year),
            date(day=31, month=5, year=ref_date.year)
        )
        summer = (
            date(day=1, month=6, year=ref_date.year),
            date(day=31, month=8, year=ref_date.year)
        )
        early_winter = (
            date(day=1, month=12, year=ref_date.year),
            date(day=28, month=2, year=ref_date.year + 1)
        )
        winter = (
            date(day=1, month=12, year=ref_date.year - 1),
            date(day=28, month=2, year=ref_date.year)
        )

        if fall[0] <= ref_date < fall[1]:
            return fall
        if summer[0] <= ref_date < summer[1]:
            return summer
        if spring[0] <= ref_date < spring[1]:
            return spring
        if early_winter[0] <= ref_date < early_winter[1]:
            return early_winter
        return winter

    else:
        spring = (
            date(day=1, month=9, year=ref_date.year),
            date(day=30, month=11, year=ref_date.year)
        )
        fall = (
            date(day=1, month=3, year=ref_date.year),
            date(day=31, month=5, year=ref_date.year)
        )
        winter = (
            date(day=1, month=6, year=ref_date.year),
            date(day=31, month=8, year=ref_date.year)
        )
        early_summer = (
            date(day=1, month=12, year=ref_date.year),
            date(day=28, month=2, year=ref_date.year + 1)
        )
        summer = (
            date(day=1, month=12, year=ref_date.year - 1),
            date(day=28, month=2, year=ref_date.year)
        )

        if fall[0] <= ref_date < fall[1]:
            return fall
        if winter[0] <= ref_date < winter[1]:
            return winter
        if spring[0] <= ref_date < spring[1]:
            return spring
        if early_summer[0] <= ref_date < early_summer[1]:
            return early_summer
        return summer


def get_week_number(ref_date=None):
    ref_date = ref_date or now_local()
    return ref_date.isocalendar()[1]
