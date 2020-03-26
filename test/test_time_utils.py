#
# Copyright 2019 Mycroft AI Inc.
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

import unittest

from lingua_franca.location import Hemisphere
from lingua_franca.time import get_season_range, get_weekend_range, \
    get_week_range, get_decade_range, get_month_range, get_year_range, \
    get_millennium_range, get_century_range, get_ordinal, get_week_number, \
    DateTimeResolution
from datetime import date
from dateutil.relativedelta import relativedelta


class TestRanges(unittest.TestCase):
    def test_range(self):
        ref_date = date(day=27, month=2, year=1994)

        weekend_range = (date(day=26, month=2, year=1994),
                         date(day=27, month=2, year=1994))
        week_range = (date(day=21, month=2, year=1994),
                      date(day=27, month=2, year=1994))
        month_range = (date(day=1, month=2, year=1994),
                       date(day=28, month=2, year=1994))
        year_range = (date(day=1, month=1, year=1994),
                      date(day=31, month=12, year=1994))
        decade_range = (date(day=1, month=1, year=1990),
                        date(day=31, month=12, year=1999))
        century_range = (date(day=1, month=1, year=1900),
                         date(day=31, month=12, year=1999))
        millennium_range = (date(day=1, month=1, year=1000),
                            date(day=31, month=12, year=1999))

        self.assertEqual(get_weekend_range(ref_date), weekend_range)
        self.assertEqual(get_week_range(ref_date), week_range)
        self.assertEqual(get_month_range(ref_date), month_range)
        self.assertEqual(get_year_range(ref_date), year_range)
        self.assertEqual(get_decade_range(ref_date), decade_range)
        self.assertEqual(get_century_range(ref_date), century_range)
        self.assertEqual(get_millennium_range(ref_date), millennium_range)

        ref_date = date(day=27, month=2, year=2112)

        weekend_range = (date(day=27, month=2, year=2112),
                         date(day=28, month=2, year=2112))
        week_range = (date(day=22, month=2, year=2112),
                      date(day=28, month=2, year=2112))
        month_range = (date(day=1, month=2, year=2112),
                       date(day=29, month=2, year=2112))
        year_range = (date(day=1, month=1, year=2112),
                      date(day=31, month=12, year=2112))
        decade_range = (date(day=1, month=1, year=2110),
                        date(day=31, month=12, year=2119))
        century_range = (date(day=1, month=1, year=2100),
                         date(day=31, month=12, year=2199))
        millennium_range = (date(day=1, month=1, year=2000),
                            date(day=31, month=12, year=2999))

        self.assertEqual(get_weekend_range(ref_date), weekend_range)
        self.assertEqual(get_week_range(ref_date), week_range)
        self.assertEqual(get_month_range(ref_date), month_range)
        self.assertEqual(get_year_range(ref_date), year_range)
        self.assertEqual(get_decade_range(ref_date), decade_range)
        self.assertEqual(get_century_range(ref_date), century_range)
        self.assertEqual(get_millennium_range(ref_date), millennium_range)


class TestOrdinals(unittest.TestCase):
    def test_first_day(self):
        ref_date = date(day=27, month=2, year=4567)
        week_start, week_end = get_week_range(ref_date)
        weekend_start, weekend_end = get_weekend_range(ref_date)

        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DAY),
                         date(day=1, month=1, year=1))
        # TODO not implemented yet
        # self.assertEqual(get_ordinal(1, ref_date,
        #                             DateTimeResolution.DAY_OF_WEEK),
        #                 week_start)
        # self.assertEqual(get_ordinal(1, ref_date,
        #                             DateTimeResolution.DAY_OF_WEEKEND),
        #                 weekend_start)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DAY_OF_MONTH),
                         ref_date.replace(day=1))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DAY_OF_YEAR),
                         ref_date.replace(day=1, month=1))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DAY_OF_DECADE),
                         date(day=1, month=1, year=4560))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DAY_OF_CENTURY),
                         date(day=1, month=1, year=4500))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DAY_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000))

    def test_first_week(self):
        ref_date = date(day=27, month=2, year=4567)

        def _test_week(n, expected_date, anchor=ref_date,
                       res=DateTimeResolution.WEEK):
            extracted = get_ordinal(n, anchor, res)
            self.assertEqual(extracted, expected_date)
            # NOTE: weeks start on sunday
            # TODO start on thursdays?
            self.assertEqual(extracted.weekday(), 0)

        week_start = date(day=1, month=1, year=1)
        _test_week(1, week_start, ref_date, DateTimeResolution.WEEK)

        _test_week(1, ref_date.replace(day=2), ref_date,
                   DateTimeResolution.WEEK_OF_MONTH)

        _test_week(1, ref_date.replace(day=5, month=1), ref_date,
                   DateTimeResolution.WEEK_OF_YEAR)

        # week started on 31 december, therefore days 1-6 belong to last
        # week of 4559
        week_start = date(day=7, month=1, year=4560)
        _test_week(1, week_start, ref_date, DateTimeResolution.WEEK_OF_DECADE)

        week_start = date(day=4, month=1, year=4500)
        _test_week(1, week_start, ref_date, DateTimeResolution.WEEK_OF_CENTURY)

        week_start = date(day=3, month=1, year=4000)
        _test_week(1, week_start, ref_date,
                   DateTimeResolution.WEEK_OF_MILLENNIUM)

    def test_first_month(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.MONTH),
                         date(day=1, month=1, year=1))

        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.MONTH_OF_YEAR),
                         ref_date.replace(day=1, month=1))

        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.MONTH_OF_DECADE),
                         date(day=1, month=1, year=4560))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.MONTH_OF_CENTURY),
                         date(day=1, month=1, year=4500))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.MONTH_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000))

    def test_first_year(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.YEAR),
                         date(day=1, month=1, year=1))

        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.YEAR_OF_DECADE),
                         date(day=1, month=1, year=4560))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.YEAR_OF_CENTURY),
                         date(day=1, month=1, year=4500))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.YEAR_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000))

    def test_first_decade(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DECADE),
                         date(day=1, month=1, year=1))

        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DECADE_OF_CENTURY),
                         date(day=1, month=1, year=4500))
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.DECADE_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000))

    def test_first_century(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.CENTURY),
                         date(day=1, month=1, year=1))

        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.CENTURY_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000))

    def test_first_millennium(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.MILLENNIUM),
                         date(day=1, month=1, year=1))

    def test_N_day(self):
        ref_date = date(day=27, month=2, year=4567)

        self.assertEqual(get_ordinal(21, ref_date,
                                     DateTimeResolution.DAY),
                         date(day=21, month=1, year=1))

        self.assertEqual(get_ordinal(12, ref_date,
                                     DateTimeResolution.DAY_OF_MONTH),
                         ref_date.replace(day=12))
        self.assertEqual(get_ordinal(21, ref_date,
                                     DateTimeResolution.DAY_OF_YEAR),
                         ref_date.replace(day=21, month=1))
        self.assertEqual(get_ordinal(12, ref_date,
                                     DateTimeResolution.DAY_OF_DECADE),
                         date(day=12, month=1, year=4560))
        self.assertEqual(get_ordinal(21, ref_date,
                                     DateTimeResolution.DAY_OF_CENTURY),
                         date(day=21, month=1, year=4500))
        self.assertEqual(get_ordinal(12, ref_date,
                                     DateTimeResolution.DAY_OF_MILLENNIUM),
                         date(day=12, month=1, year=4000))

    def test_N_week(self):
        ref_date = date(day=27, month=2, year=4567)

        def _test_week(n, expected_date, anchor=ref_date,
                       res=DateTimeResolution.WEEK):
            extracted = get_ordinal(n, anchor, res)
            self.assertEqual(extracted, expected_date)
            # NOTE: weeks start on sunday
            # TODO start on thursdays?
            self.assertEqual(extracted.weekday(), 0)

        week_start = date(day=15, month=1, year=1)
        _test_week(3, week_start, ref_date, DateTimeResolution.WEEK)

        _test_week(3, ref_date.replace(day=16), ref_date,
                   DateTimeResolution.WEEK_OF_MONTH)

        _test_week(3, ref_date.replace(day=19, month=1), ref_date,
                   DateTimeResolution.WEEK_OF_YEAR)

        week_start = date(day=21, month=1, year=4560)
        _test_week(3, week_start, ref_date, DateTimeResolution.WEEK_OF_DECADE)

        week_start = date(day=18, month=1, year=4500)
        _test_week(3, week_start, ref_date, DateTimeResolution.WEEK_OF_CENTURY)

        week_start = date(day=17, month=1, year=4000)
        _test_week(3, week_start, ref_date,
                   DateTimeResolution.WEEK_OF_MILLENNIUM)

    def test_N_month(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(10, ref_date,
                                     DateTimeResolution.MONTH),
                         date(day=1, month=10, year=1))

        self.assertEqual(get_ordinal(11, ref_date,
                                     DateTimeResolution.MONTH_OF_YEAR),
                         ref_date.replace(day=1, month=11))

        self.assertEqual(get_ordinal(25, ref_date,
                                     DateTimeResolution.MONTH_OF_DECADE),
                         date(day=1, month=1, year=4560) +
                         relativedelta(months=24))
        self.assertEqual(get_ordinal(71, ref_date,
                                     DateTimeResolution.MONTH_OF_CENTURY),
                         date(day=1, month=1, year=4500) +
                         relativedelta(months=70))
        self.assertEqual(get_ordinal(109, ref_date,
                                     DateTimeResolution.MONTH_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000) +
                         relativedelta(months=108))

    def test_N_year(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(1, ref_date,
                                     DateTimeResolution.YEAR),
                         date(day=1, month=1, year=1))

        self.assertEqual(get_ordinal(7, ref_date,
                                     DateTimeResolution.YEAR_OF_DECADE),
                         date(day=1, month=1, year=4560) +
                         relativedelta(years=6))
        self.assertEqual(get_ordinal(36, ref_date,
                                     DateTimeResolution.YEAR_OF_CENTURY),
                         date(day=1, month=1, year=4500) +
                         relativedelta(years=35))
        self.assertEqual(get_ordinal(156, ref_date,
                                     DateTimeResolution.YEAR_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000) +
                         relativedelta(years=155))

    def test_N_decade(self):
        ref_date = date(day=27, month=2, year=4567)

        self.assertEqual(get_ordinal(8, ref_date,
                                     DateTimeResolution.DECADE),
                         date(day=1, month=1, year=70))

        self.assertEqual(get_ordinal(9, ref_date,
                                     DateTimeResolution.DECADE_OF_CENTURY),
                         date(day=1, month=1, year=4500) +
                         relativedelta(years=80))
        self.assertEqual(get_ordinal(18, ref_date,
                                     DateTimeResolution.DECADE_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000) +
                         relativedelta(years=170))

    def test_N_century(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertEqual(get_ordinal(21, ref_date,
                                     DateTimeResolution.CENTURY),
                         date(day=1, month=1, year=2000))

        self.assertEqual(get_ordinal(10, ref_date,
                                     DateTimeResolution.CENTURY_OF_MILLENNIUM),
                         date(day=1, month=1, year=4000) +
                         relativedelta(years=900))

    def test_N_millennium(self):
        self.assertEqual(get_ordinal(10,
                                     resolution=DateTimeResolution.MILLENNIUM),
                         date(day=1, month=1, year=9000))

    def test_last_day(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.DAY)

        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DAY_OF_MONTH),
                         ref_date.replace(day=28))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DAY_OF_YEAR),
                         ref_date.replace(day=31, month=12))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DAY_OF_DECADE),
                         date(day=31, month=12, year=4569))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DAY_OF_CENTURY),
                         date(day=31, month=12, year=4599))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DAY_OF_MILLENNIUM),
                         date(day=31, month=12, year=4999))

    def test_last_week(self):
        ref_date = date(day=27, month=2, year=4567)

        def _test_week(n, expected_date, anchor=ref_date,
                       res=DateTimeResolution.WEEK):
            extracted = get_ordinal(n, anchor, res)
            self.assertEqual(extracted, expected_date)
            # NOTE: weeks start on sunday
            # TODO start on thursdays?
            self.assertEqual(extracted.weekday(), 0)

        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.WEEK)

        _test_week(-1, ref_date.replace(day=23), ref_date,
                   DateTimeResolution.WEEK_OF_MONTH)

        _test_week(-1, ref_date.replace(day=28, month=12), ref_date,
                   DateTimeResolution.WEEK_OF_YEAR)

        # week started on 31 december, therefore days 1-6 belong to last
        # week of 4559
        week_start = date(day=25, month=12, year=4569)
        _test_week(-1, week_start, ref_date, DateTimeResolution.WEEK_OF_DECADE)

        week_start = date(day=30, month=12, year=4599)
        _test_week(-1, week_start, ref_date,
                   DateTimeResolution.WEEK_OF_CENTURY)

        week_start = date(day=30, month=12, year=4999)
        _test_week(-1, week_start, ref_date,
                   DateTimeResolution.WEEK_OF_MILLENNIUM)

    def test_last_month(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.MONTH)

        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.MONTH_OF_YEAR),
                         ref_date.replace(day=1, month=12))

        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.MONTH_OF_DECADE),
                         date(day=1, month=12, year=4569))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.MONTH_OF_CENTURY),
                         date(day=1, month=12, year=4599))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.MONTH_OF_MILLENNIUM),
                         date(day=1, month=12, year=4999))

    def test_last_year(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.YEAR)

        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.YEAR_OF_DECADE),
                         date(day=1, month=1, year=4569))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.YEAR_OF_CENTURY),
                         date(day=1, month=1, year=4599))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.YEAR_OF_MILLENNIUM),
                         date(day=1, month=1, year=4999))

    def test_last_decade(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.DECADE)

        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DECADE_OF_CENTURY),
                         date(day=1, month=1, year=4590))
        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.DECADE_OF_MILLENNIUM),
                         date(day=1, month=1, year=4990))

    def test_last_century(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.CENTURY)

        self.assertEqual(get_ordinal(-1, ref_date,
                                     DateTimeResolution.CENTURY_OF_MILLENNIUM),
                         date(day=1, month=1, year=4900))

    def test_last_millennium(self):
        ref_date = date(day=27, month=2, year=4567)
        self.assertRaises(OverflowError, get_ordinal, -1, ref_date,
                          DateTimeResolution.MILLENNIUM)


class TestHemisphere(unittest.TestCase):
    def test_north(self):
        start_spring = date(day=1, month=3, year=2117)
        start_summer = date(day=1, month=6, year=2117)
        start_fall = date(day=1, month=9, year=2117)
        start_winter = date(day=1, month=12, year=2117)

        end_spring = date(day=31, month=5, year=2117)
        end_summer = date(day=31, month=8, year=2117)
        end_fall = date(day=30, month=11, year=2117)
        end_winter = date(day=28, month=2, year=2118)

        spring = date(day=20, month=4, year=2117)
        summer = date(day=20, month=8, year=2117)
        fall = date(day=20, month=10, year=2117)
        winter = date(day=30, month=12, year=2117)
        late_winter = date(day=20, month=2, year=2118)

        hemi = Hemisphere.NORTH

        def _test_range(test_date, expected_start, expect_end):
            start, end = get_season_range(test_date, hemi)
            self.assertEqual(start, expected_start)
            self.assertEqual(end, expect_end)

        _test_range(spring, start_spring, end_spring)

        _test_range(fall, start_fall, end_fall)

        _test_range(summer, start_summer, end_summer)

        _test_range(winter, start_winter, end_winter)

        _test_range(late_winter, start_winter, end_winter)

    def test_south(self):
        start_spring = date(day=1, month=9, year=2117)
        start_summer = date(day=1, month=12, year=2117)
        start_fall = date(day=1, month=3, year=2117)
        start_winter = date(day=1, month=6, year=2117)

        end_spring = date(day=30, month=11, year=2117)
        end_winter = date(day=31, month=8, year=2117)
        end_fall = date(day=31, month=5, year=2117)
        end_summer = date(day=28, month=2, year=2118)

        fall = date(day=20, month=4, year=2117)
        winter = date(day=20, month=8, year=2117)
        spring = date(day=20, month=10, year=2117)
        summer = date(day=30, month=12, year=2117)
        late_summer = date(day=20, month=2, year=2118)

        hemi = Hemisphere.SOUTH

        def _test_range(test_date, expected_start, expect_end):
            start, end = get_season_range(test_date, hemi)
            self.assertEqual(start, expected_start)
            self.assertEqual(end, expect_end)

        _test_range(spring, start_spring, end_spring)

        _test_range(fall, start_fall, end_fall)

        _test_range(winter, start_winter, end_winter)

        _test_range(summer, start_summer, end_summer)

        _test_range(late_summer, start_summer, end_summer)


if __name__ == "__main__":
    unittest.main()
