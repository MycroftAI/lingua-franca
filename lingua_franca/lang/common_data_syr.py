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

_FUNCTION_NOT_IMPLEMENTED_WARNING = "ܐܗܐ ܣܘܥܪܢܐ ܠܐ ܝܠܗ ܦܝܫܐ ܬܘܡܡܐ ܒܠܫܢܐ ܣܘܪܝܝܐ"

# Word rules for gender
_SYRIAC_FEMALE_ENDINGS = ["ܬܐ"]
_SYRIAC_MALE_ENDINGS = ["ܐ"]

# Special cases, word lookup for words not covered by above rule

# Masculine gender denotes names of: 
#	- rivers, islands, days of the week (except:Saturday and Sunday)
#	- words where the letter ܬ does not appear as a suffix, but as part of
#	  the root (ܒܝܬܐ، ܡܘܬܐ)
#	- loanwords with penultimate letter ܬ referring to masculine gender
#	  such as ܐܟܬܐ
                                                                       
_SYRIAC_GENDERED_NOUNS_EXCEPTIONS = {
	"ܥܪܘܒܬܐ": "f",
	"ܫܒܬܐ": "f",
    "ܕܩܠܬ": "m",
    "ܦܪܬ": "m",
    "ܒܝܬܐ": "m",
    "ܡܘܬܐ": "m"
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
    "ܬܫܥܣܪ"
]

_SYRIAC_ONES_FEM = [
    "",
    "ܚܕܐ",
    "ܬܪܬܝܢ",
    "ܬܠܬ",
    "ܐܪܒܥ",
    "ܚܡܫ",
    "ܫܬ",
    "ܫܒܥ",
    "ܬܡܢܐ",
    "ܬܫܥ"
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
    "ܬܫܥܝܢ"
]

_SYRIAC_HUNDREDS = [
    "",
    "ܡܐܐ",
    "ܬܪܝܢܡܐܐ",
    "ܬܠܬܡܐܐ",
    "ܐܪܒܥܡܐܐ",
    "ܚܡܫܡܐܐ",
    "ܫܬܡܐܐ",
    "ܫܒܥܡܐܐ",
    "ܬܡܢܡܐܐ",
    "ܬܫܥܡܐܐ"
]

_SYRIAC_LARGE = [
    "",
    "ܐܠܦܐ",
    "ܡܠܝܘܢܐ",
    "ܡܠܝܪܐ",
    "ܒܠܝܘܢܐ",
    "ܒܠܝܪܐ"
]

_SYRIAC_ORDINAL_BASE = {
    1: 'ܩܕܡܝܐ',
    2: 'ܬܪܝܢܐ',
    3: 'ܬܠܝܬܝܐ',
    4: 'ܪܒܝܥܝܐ',
    5: 'ܚܡܝܫܝܐ',
    6: 'ܫܬܝܬܝܐ',
    7: 'ܫܒܝܥܝܐ',
    8: 'ܬܡܝܢܝܐ',
    9: 'ܬܫܝܥܝܐ',
    10: 'ܥܣܝܪܝܐ',
    11: 'ܚܕܥܣܝܪܝܐ',
    12: 'ܬܪܥܣܝܪܝܐ',
    13: 'ܬܠܬܥܣܝܪܝܐ',
    14: 'ܐܪܒܥܣܝܪܝܐ',
    15: 'ܚܡܫܥܣܝܪܝܐ',
    16: 'ܫܬܥܣܝܪܝܐ',
    17: 'ܫܒܥܣܝܪܝܐ',
    18: 'ܬܡܢܥܣܝܪܝܐ',
    19: 'ܬܫܥܣܝܪܝܐ',
    20: 'ܥܣܪܝܢܝܐ',
    30: 'ܬܠܬܝܢܝܐ',
    40: 'ܐܪܒܥܝܢܝܐ',
    50: 'ܚܡܫܝܢܝܐ',
    60: 'ܫܬܝܢܝܐ',
    70: 'ܫܒܥܝܢܝܐ',
    80: 'ܬܡܢܝܢܝܐ',
    90: 'ܬܫܥܝܢܝܐ',
    100: 'ܐܡܝܐ',
    200: 'ܬܪܝܢܡܝܐ',
    300: 'ܬܠܬܡܝܐ',
    400: 'ܐܪܒܥܡܝܐ',
    500: 'ܚܡܫܡܝܐ',
    600: 'ܫܬܡܝܐ',
    700: 'ܫܒܥܡܝܐ',
    800: 'ܬܡܢܡܝܐ',
    900: 'ܬܫܥܡܝܐ',
    1000: 'ܐܠܦܝܐ',
    10000: 'ܪܒܘܬܢܝܐ'
}

_SYRIAC_FRACTIONS = {
    3: "ܬܘܠܬܐ",
    4: "ܪܘܒܥܐ",
    5: "ܚܘܡܫܐ",
    6: "ܫܘܬܬܐ",
    7: "ܫܘܒܥܐ",
    8: "ܬܘܡܢܐ",
    9: "ܬܘܫܥܐ",
    10: "ܥܘܣܪܐ",
    20: "ܚܕ ܡܢ ܥܣܪܝܢ",
    30: "ܚܕ ܡܢ ܬܠܬܝܢ",
    50: "ܚܕ ܡܢ ܚܡܫܝܢ",
    100: "ܚܕ ܡܢ ܡܐܐ",
    1000: "ܚܕ ܡܢ ܐܠܦܐ"
}

_SYRIAC_FRACTIONS_HALF = [
    "ܦܠܓܐ",
    "ܦܠܓܗ",
    "ܦܠܓܘ",
    "ܦܠܓܘܬ"
]

_SYRIAC_FRAC = ["", "ܥܣܪܐ", "ܡܐܐ"]
_SYRIAC_FRAC_BIG = ["", "ܐܠܦܐ", "ܡܠܝܘܢܐ", "ܒܠܝܘܢܐ" ]

# Fraction separator
_SYRIAC_SEPARATOR = " ܡܢ "

# Conjoiner
_SYRIAC_CONJOINER = " ܘ"