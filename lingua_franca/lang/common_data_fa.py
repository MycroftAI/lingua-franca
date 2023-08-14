#
# Copyright 2017 Mycroft AI Inc.
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
from collections import OrderedDict
from .parse_common import invert_dict

_FUNCTION_NOT_IMPLEMENTED_WARNING = "تابع خواسته شده در زبان فارسی پیاده سازی نشده است."

_NUM_STRING_FA = {
    0: 'صفر',
    1: 'یک',
    2: 'دو',
    3: 'سه',
    4: 'چهار',
    5: 'پنج',
    6: 'شش',
    7: 'هفت',
    8: 'هشت',
    9: 'نه',
    10: 'ده',
    11: 'یازده',
    12: 'دوازده',
    13: 'سیزده',
    14: 'چهارده',
    15: 'پانزده',
    16: 'شانزده',
    17: 'هفده',
    18: 'هجده',
    19: 'نوزده'
}
_SUMS_FARSI = {
    20: 'بیست',
    30: 'سی',
    40: 'چهل',
    50: 'پنجاه',
    60: 'شصت',
    70: 'هفتاد',
    80: 'هشتاد',
    90: 'نود',
    100: 'صد',
    200: 'دویست',
    300: 'سیصد',
    400: 'چهارصد',
    500: 'پانصد',
    600: 'ششصد',
    700: 'هفصد',
    800: 'هشصد',
    900: 'نهصد',
    1000: 'هزار'
}
_FRACTION_STRING_FA = {
    1: 'یکم',
    2: 'دوم',
    3: 'سوم',
    4: 'چهارم',
    5: 'پنجم',
    6: 'ششم',
    7: 'هفتم',
    8: 'هشتم',
    9: 'نهم',
    10: 'دهم',
    11: 'یازدهم',
    12: 'دوازدهم',
    13: 'سیزدهم',
    14: 'چهاردهم',
    15: 'پانزدهم',
    16: 'شونزدهم',
    17: 'هفدهم',
    18: 'هجدهم',
    19: 'نوزدهم',
    20: 'بیستم'
}
_SCALE_FA = OrderedDict([
    (1000, 'هزار'),
    (1000000, 'میلیون'),
    (1e9, "میلیارد"),
    (1e12, 'تریلیون'),
    (1e15, "کوادریلیون"),
    (1e18, "کوئینتیلیون"),
    (1e21, "سکتلیون"),
    (1e24, "سپتیلیون"),
    (1e27, "اکتیلیون"),
    (1e30, "ننیلیون"),
    (1e33, "دسیلیون")
])
_ORDINAL_BASE_FA = {
    1: 'یکم',
    2: 'دوم',
    3: 'سوم',
    4: 'چهارم',
    5: 'پنجم',
    6: 'ششم',
    7: 'هفتم',
    8: 'هشتم',
    9: 'نهم',
    10: 'دهم',
    11: 'یازدهم',
    12: 'دوازدهم',
    13: 'سیزدهم',
    14: 'چهاردهم',
    15: 'پانزدهم',
    16: 'شانزدهم',
    17: 'هفدهم',
    18: 'هجدهم',
    19: 'نوزدهم',
    20: 'بیستم',
    30: 'سیم',
    40: "چهلم",
    50: "پنجاهم",
    60: "شصتم",
    70: "هفتادم",
    80: "هشتادم",
    90: "نودم",
    1e2: "صدم",
    1e3: "هزارم"
}
_ORDINAL_FA = {
    1e6: "میلیونم",
    1e9: "میلیاردم",
    1e12: "تریلیونم",
    1e15: "کوادریلیونم",
    1e18: "کوئینتیلیونم",
    1e21: "سکتلیونم",
    1e24: "سپتیلیونم",
    1e27: "اکتیلیونم",
    1e30: "ننیلیونم",
    1e33: "دسیلیونم"
}
_ORDINAL_FA.update(_ORDINAL_BASE_FA)

_DECIMAL_MARKER_FA = {"و"}

_DECIMAL_STRING_FA = {
    1: "دهم",
    2: "صدم",
    3: "هزارم",
    6: "میلیونم",
    9: "میلیاردم",
}
_FARSI_SUMS = invert_dict(_SUMS_FARSI)
_NUM_STRING_FA.update(_SUMS_FARSI)
_STRING_NUM_FA = invert_dict(_NUM_STRING_FA)

_NEGATIVES_FA = {"منفی"}

_EXTRA_SPOKEN_NUM_FA = {
        "نیم": 2
        }
_STRING_ORDINAL_FA = invert_dict(_ORDINAL_FA)
_STRING_ORDINAL_FA.update(invert_dict(_ORDINAL_BASE_FA))
_STRING_SCALE_FA = invert_dict(_SCALE_FA)
_STRING_FRACTION_FA = invert_dict(_FRACTION_STRING_FA)
_STRING_DECIMAL_FA = invert_dict(_DECIMAL_STRING_FA)
