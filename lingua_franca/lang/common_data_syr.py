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

_FUNCTION_NOT_IMPLEMENTED_WARNING = "ܐܵܗܵܐ ܣܘܼܥܪܵܢܵܐ ܠܸܐ ܝܠܸܗ ܦܝܸܫܵܐ ܬܘܼܡܸܡܵܐ ܒܠܸܫܵܢܵܐ ܣܘܼܪܝܵܝܵܐ"

_FRACTION_STRING_SYR = {
    2: 'ܬܪܲܝܵܢܵܐ',
    3: 'ܬܠܝܼܬܵܝܵܐ',
    4: 'ܪܒ݂ܝܼܥܵܝܵܐ',
    5: 'ܚܡܝܼܫܵܝܵܐ',
    6: 'ܫܬܝܼܬܵܝܵܐ',
    7: 'ܫܒ݂ܝܼܥܵܝܵܐ',
    8: 'ܬܡܝܼܢܵܝܵܐ',
    9: 'ܬܫܝܼܥܵܝܵܐ',
    10: 'ܥܣܝܼܪܵܝܵܐ',
    11: 'ܚܲܕܥܣܝܼܪܵܝܵܐ',
    12: 'ܬܪܸܥܣܝܼܪܵܝܵܐ',
    13: 'ܬܠܵܬܥܣܝܼܪܵܝܵܐ',
    14: 'ܐܲܪܒܲܥܣܝܼܪܵܝܵܐ',
    15: 'ܚܲܡܫܲܥܣܝܼܪܵܝܵܐ',
    16: 'ܫܬܲܥܣܝܼܪܵܝܵܐ',
    17: 'ܫܒܲܥܣܝܼܪܵܝܵܐ',
    18: 'ܬܡܵܢܲܥܣܝܼܪܵܝܵܐ',
    19: 'ܬܫܲܥܣܝܼܪܵܝܵܐ',
    20: 'ܥܸܣܪܝܼܢܵܝܵܐ',
}

_SYRIAC_ONES = [
    "",
    "ܚܕ",
    "ܬܪܹܝܢ",
    "ܬܠܵܬܵܐ",
    "ܐܲܪܒܥܵܐ",
    "ܚܲܡܫܵܐ",
    "ܫܬܵܐ",
    "ܫܲܒ݂ܥܵܐ",
    "ܬܡܵܢܝܵܐ",
    "ܬܸܫܥܵܐ",
    "ܥܸܣܪܵܐ",
    "ܚܕܥܣܲܪ",
    "ܬܪܸܥܣܲܪ",
    "ܬܠܵܬܲܥܣܲܪ",
    "ܐܲܪܒܲܥܣܲܪ",
    "ܚܲܡܫܲܥܣܲܪ",
    "ܫܬܲܥܣܲܪ",
    "ܫܒܲܥܣܲܪ",
    "ܬܡܵܢܲܥܣܲܪ",
    "ܬܫܲܥܣܲܪ",
]

_SYRIAC_TENS = [
    "",
    "ܥܸܣܪܵܐ",
    "ܥܸܣܪܝܼܢ",
    "ܬܠܵܬܝܼܢ",
    "ܐܲܪܒܥܝܼܢ",
    "ܚܲܡܫܝܼܢ",
    "ܫܬܝܼܢ",
    "ܫܲܒ݂ܥܝܼܢ",
    "ܬܡܵܢܝܼܢ",
    "ܬܸܫܥܝܼܢ",
]

_SYRIAC_HUNDREDS = [
    "",
    "ܡܵܐܐ",
    "ܬܪܹܝܢܡܵܐܐ",
    "ܬܠܵܬܡܵܐܐ",
    "ܐܲܪܒܲܥܡܵܐܐ",
    "ܚܲܡܫܲܡܵܐܐ",
    "ܫܬܲܡܵܐܐ",
    "ܫܒܲܥܡܵܐܐ",
    "ܬܡܵܢܹܡܵܐܐ",
    "ܬܫܲܥܡܵܐܐ",
]

_SYRIAC_LARGE = [
    "",
    "ܐܲܠܦܵܐ",  
    "ܪܸܒܘܼܬ݂ܵܐ",
    "ܡܵܐܐ ܕܐܲܠܦܝ̈ܢ",
    "ܡܸܠܝܘܿܢܵܐ",
    "ܡܸܠܝܵܪܵܐ",
    "ܒܸܠܝܘܿܢܵܐ",
    "ܒܸܠܝܵܪܵܐ",
]

_SYRIAC_ORDINALS = [
    "ܩܲܕܡܵܝܵܐ",
    "ܬܪܲܝܵܢܵܐ",
    "ܬܠܼܝܬܵܝܵܐ",
    "ܪܒ݂ܝܼܥܵܝܵܐ",
    "ܚܡܝܼܫܵܝܵܐ",
    "ܫܬܝܼܬܵܝܵܐ",
    "ܫܒ݂ܝܼܥܵܝܵܐ",
    "ܬܡܝܼܢܵܝܵܐ",
    "ܬܫܝܼܥܵܝܵܐ",
    "ܥܣܝܼܪܵܝܵܐ",
    "ܚܕܥܣܝܼܪܵܝܵܐ",
    "ܬܪܸܥܣܝܼܪܵܝܵܐ",
    "ܬܠܵܬܥܣܝܼܪܵܝܵܐ",
    "ܐܲܪܒܲܥܣܝܼܪܵܝܵܐ",
    "ܚܲܡܫܲܥܣܝܼܪܵܝܵܐ",
    "ܫܬܲܥܣܝܼܪܵܝܵܐ",
    "ܫܒܲܥܣܝܼܪܵܝܵܐ",
    "ܬܡܵܢܲܥܣܝܼܪܵܝܵܐ",
    "ܬܫܲܥܣܝܼܪܵܝܵܐ",
    "ܥܸܣܪܝܼܢܵܝܵܐ",
    "ܠܬܵܠܝܼܢܵܝܵܐ",
    "ܐܲܪܒܥܝܼܢܵܝܵܐ",
    "ܚܲܡܫܝܼܢܵܝܵܐ",
    "ܫܬܝܼܢܵܝܵܐ",
    "ܫܵܒ݂ܥܝܼܢܵܝܵܐ",
    "ܬܡܵܢܝܼܢܵܝܵܐ",
    "ܬܸܫܥܝܼܢܵܝܵܐ",
    "ܐܸܡܵܝܵܐ",
    "ܐܲܠܦܵܝܵܐ",
]

_SYRIAC_FRAC = ["", "ܥܸܣܪܵܐ", "ܡܵܐܐ"]
_SYRIAC_FRAC_BIG = ["", "ܐܲܠܦܵܐ", "ܡܸܠܝܘܿܢܵܐ", "ܒܸܠܝܘܿܢܵܐ" ]

# fraction separator
_SYRIAC_SEPARATOR = "ܡܢ"
