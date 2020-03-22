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

from lingua_franca.lang.parse_common import Hemisphere
from lingua_franca.time import get_season_range
from datetime import date


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
