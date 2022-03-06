·#
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

_FUNCTION_NOT_IMPLEMENTED_WARNING = "ܐܗܐ ܣܘܥܪܢܐ ܠܐ ܝܠܗ ܦܝܫܐ ܬܘܡܡܐ ܒܠܫܢܐ ܣܘܪܝܝܐ"

_FRACTION_STRING_SYR = {
    2: 'ܬܪܝܢܐ',
    3: 'ܬܠܝܬܝܐ',
    4: 'ܪܒܝܥܝܐ',
    5: 'ܚܡܝܫܝܐ',
    6: 'ܫܬܝܬܝܐ',
    7: 'ܫܒܝܥܝܐ',
    8: 'ܬܡܝܢܥܐ',
    9: 'ܬܫܝܥܝܐ',
    10: 'ܥܣܝܪܝܐ',
    11: 'ܚ̄ܕܥܣܝܪܝܐ',
    12: 'ܬܪܥܣܝܪܝܐ',
    13: 'ܬܠܬܥܣܝܪܝܐ',
    14: 'ܐܪܒܥܣܝܪܝܐ',
    15: 'ܚܡܫܥܣܝܪܝܐ',
    16: 'ܫܬܥܣܝܪܝܐ',
    17: 'ܫܒܥܣܝܪܝܐ',
    18: 'ܬܡܢܥܣܝܪܝܐ',
    19: 'ܬܫܥܣܝܪܝܐ',
    20: 'ܥܣܪܝܢܝܐ',
}

_SYRIAC_ONES = [
    "",
    "ܚܕ",
    "ܬܪܝܢ",
    "ܬܠܬܐ",
    "ܐܪܒܥܐ",
    "ܚܡܫܐ",
    "ܫܬܐ",
    "ܫܒܥܐ",
    "ܬܡܢܝܐ",
    "ܬܫܥܐ",
    "ܥܣܪܐ",
    "ܚܕܥܣܪ",
    "ܬܪܥܣܪ",
    "ܬܠܬܥܣܪ",
    "ܐܪܒܥܣܪ",
    "ܚܡܫܥܣܪ",
    "ܫܬܥܣܪ",
    "ܫܒܥܣܪ",
    "ܬܡܢܥܣܪ",
    "ܬܫܥܣܪ",
]

_SYRIAC_TENS = [
    "",
    "ܥܣܪܐ",
    "ܥܣܪܝܢ",
    "ܬܠܬܝܢ",
    "ܐܪܒܥܝܢ",
    "ܚܡܫܝܢ",
    "ܫܬܝܢ",
    "ܫܒܥܝܢ",
    "ܬܡܢܝܢ",
    "ܬܫܥܝܢ",
]

_SYRIAC_HUNDREDS = [
    "",
    "ܡܐܐ",
    "ܬܪܝܡܐܐ",
    "ܬܠܬܡܐܐ",
    "ܐܪܒܥܡܐܐ",
    "ܚܡܫܡܐܐ",
    "ܫܬܡܐܐ",
    "ܫܒܥܡܐܐ",
    "ܬܡܢܡܐܐ",
    "ܬܫܥܡܐܐ",
]

_SYRIAC_LARGE = [
    "",
    "ܐܠܦܐ",
    "ܪܒܘܬܐ",
    "ܡܠܝܘܢ",
    "ܒܠܝܘܢ",
    "ܬܪܠܝܐܢ",
    "ܡܠܝܪܕ",
]

_SYRIAC_ORDINALS = [
    "ܩܕܡܝܐ",
    "ܬܪܝܢܐ",
    "ܬܠܝܬܝܐ",
    "ܪܒܝܥܝܐ",
    "ܚܡܝܫܝܐ",
    "ܫܬܝܬܝܐ",
    "ܫܒܝܥܝܐ",
    "ܬܡܝܢܝܐ",
    "ܬܫܝܥܝܐ",
    "ܥܣܝܪܝܐ",
    "ܚܕ̄ܥܣܝܪܝܐ",
    "ܬܪܥܣܝܪܝܐ",
    "ܬܠܬܥܣܝܪܝܐ",
    "ܐܪܒܥܣܝܪܝܐ",
    "ܚܡܫܥܣܝܪܝܐ",
    "ܫܬܥܣܝܪܝܐ",
    "ܫܒܥܣܝܪܝܐ",
    "ܬܡܢܥܣܝܪܝܐ",
    "ܬܫܥܣܝܪܝܐ",
    "ܥܣܪܝܢܝܐ",
    "ܠܬܠܝܢܝܐ",
    "ܐܪܒܥܝܢܝܐ",
    "ܚܡܫܝܢܝܐ",
    "ܫܬܝܢܝܐ",
    "ܫܒܥܝܢܝܐ",
    "ܬܡܢܝܢܝܐ",
    "ܬܫܥܝܢܝܐ",
    "ܐܡܝܐ",
    "ܐܠܦܝܐ",
]

_SYRIAC_FRAC = ["", "ܥܣܪܐ", "ܡܐܐ"]
_SYRIAC_FRAC_BIG = ["", "ܐܠܦܐ", "ܡܠܝܘܢ", "ܒܠܝܘܢ" ]

# fraction separator
_SYRIAC_SEPARATOR = "ܡܢ"
