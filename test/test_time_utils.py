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
    get_millennium_range, get_century_range, get_ordinal, get_week_number
from datetime import date


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
