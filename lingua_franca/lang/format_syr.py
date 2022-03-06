# -*- coding: utf-8 -*-
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

from lingua_franca.lang.format_common import convert_to_mixed_fraction
from lingua_franca.lang.common_data_syr import \
    _SYRIAC_ONES, _SYRIAC_TENS, _SYRIAC_HUNDREDS, _SYRIAC_LARGE, \   
    _SYRIAC_SEPARATOR, _SYRIAC_FRAC, _SYRIAC_FRAC_BIG, _FRACTION_STRING_SYR
import math
from lingua_franca.internal import lookup_variant
from enum import IntEnum
from functools import wraps


def nice_number_syr(number, speech=True, denominators=range(1, 21), variant=None):
    """ Syriac helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "4 and a half" for speech and "4 1/2" for text

    Args:
        number (int or float): the float to format
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """

    result = convert_to_mixed_fraction(number, denominators)
    if not result:
        # Give up, just represent as a 3 decimal number
        return str(round(number, 3))

    whole, num, den = result

    if not speech:
        if num == 0:
            # TODO: Number grouping?  E.g. "1,000,000"
            return str(whole)
        else:
            return '{} {}/{}'.format(whole, num, den)

    if num == 0:
        return str(whole)
    den_str = _FRACTION_STRING_SYR[den]
    if whole == 0:
        if num == 1:
            return_string = 'ܚܕ {}'.format(den_str)
        else:
            return_string = '{} {}'.format(num, den_str)
    elif num == 1:
        return_string = '{} ܘ ܚܕ {}'.format(whole, den_str)
    else:
        return_string = '{} ܘ {} {}'.format(whole, num, den_str)
    return return_string


def _float2tuple(value, _precision):
    pre = int(value)

    post = abs(value - pre) * 10**_precision
    if abs(round(post) - post) < 0.01:
        # We generally floor all values beyond our precision (rather than
        # rounding), but in cases where we have something like 1.239999999,
        # which is probably due to python's handling of floats, we actually
        # want to consider it as 1.24 instead of 1.23
        post = int(round(post))
    else:
        post = int(math.floor(post))

    while post != 0:
        x, y = divmod(post, 10)
        if y != 0:
            break
        post = x
        _precision -= 1

    return pre, post, _precision


def _cardinal3(number):
    if (number < 19):
        return _SYRIAC_ONES[number]
    if (number < 100):
        x, y = divmod(number, 10)
        if y == 0:
            return _SYRIAC_TENS[x]
        return _SYRIAC_TENS[x] + _SYRIAC_SEPARATOR + _SYRIAC_ONES[y] 
    x, y = divmod(number, 100)
    if y == 0:
        return _SYRIAC_HUNDREDS[x]
    return _SYRIAC_HUNDREDS[x] + _SYRIAC_SEPARATOR + _cardinal3(y)

def _cardinalPos(number):
    x = number
    res = ''
    for b in _SYRIAC_LARGE:
        x, y = divmod(x, 1000)
        if (y == 0):
            continue
        yx = _cardinal3(y)
        if y == 1 and b == 'ܐܠܦܐ':
            yx = b
        elif b != '':
            yx += ' ' + b
        if (res == ''):
            res = yx
        else:
            res = yx + _SYRIAC_SEPARATOR + res
    return res

def _fractional(number, l):
    if (number / 10**l == 0.5):
        return "ܦܠܓܗ"
    x = _cardinalPos(number)
    ld3, lm3 = divmod(l, 3)
    ltext = (_SYRIAC_FRAC[lm3] + " " + _SYRIAC_FRAC_BIG[ld3]).strip() + 'م'
    return x + " " + ltext

def _to_ordinal(number):
    r = _to_cardinal(number, 0)
    if (r[-1] == 'ه' and r[-2] == 'ܫ'):
        return r[:-1] + 'ܘܡ'
    return r + 'ܡ'

def _to_ordinal_num(value):
    return str(value)+"ܡ"

def _to_cardinal(number, places):
    if number < 0:
        return "ܣܚܘܦܐ " + _to_cardinal(-number, places)
    if (number == 0):
        return "ܣܝܦܪ"
    x, y, l = _float2tuple(number, places)
    if y == 0:
        return _cardinalPos(x)
    if x == 0:
        return _fractional(y, l)
    return _cardinalPos(x) + _SYRIAC_SEPARATOR + _fractional(y, l)

def pronounce_number_syr(number, places=2, scientific=False,
                        ordinals=False, variant=None):
    """
    Convert a number to it's spoken equivalent

    For example, '5.2' would return 'five point two'

    Args:
        num(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
        scientific (bool): pronounce in scientific notation
        ordinals (bool): pronounce in ordinal form "first" instead of "one"
    Returns:
        (str): The pronounced number
    """
    num = number
    # deal with infinity
    if num == float("inf"):
        return "ܠܐ ܡܬܚܡܐ"
    elif num == float("-inf"):
        return "ܣܚܘܦܐ ܠܐ ܡܬܚܡܐ"
    if scientific:
        if number == 0:
            return "ܣܝܦܪ"
        number = '%E' % num
        n, power = number.replace("+", "").split("E")
        power = int(power)
        if power != 0:
            return '{}{} ܫܪܬܚ ܥܣܪܐ ܒܚܝܠܐ {}{}'.format(
                'ܣܚܘܦܐ ' if float(n) < 0 else '',
                pronounce_number_syr(
                    abs(float(n)), places, False, ordinals=False),
                'ܣܚܘܦܐ ' if power < 0 else '',
                pronounce_number_syr(abs(power), places, False, ordinals=False))
    if ordinals:
        return _to_ordinal(number)
    return _to_cardinal(number, places)
    
def nice_time_syr(dt, speech=True, use_24hour=False, use_ampm=False, variant=None):
    """
    Format a time to a comfortable human format
    For example, generate 'five thirty' for speech or '5:30' for
    text display.
    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""

        # Either "0 8 hundred" or "13 hundred"
        if string[0] == '0':
            speak += pronounce_number_syr(int(string[1]))
        else:
            speak = pronounce_number_syr(int(string[0:2]))
        if not string[3:5] == '00':
            speak += " ܘ "
            if string[3] == '0':
                speak += pronounce_number_syr(int(string[4]))
            else:
                speak += pronounce_number_syr(int(string[3:5]))
            speak += ' ܩܛܝܢ̈ܬ̣ܐ'
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "ܛܗܪ̈ܝ ܠܠܝܐ"
        elif dt.hour == 12 and dt.minute == 0:
            return "ܛܗܪܐ"

        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 15:
            speak = pronounce_number_syr(hour) + " ܘܪܘܒܥܐ"
        elif dt.minute == 30:
            speak = pronounce_number_syr(hour) + " ܘܦܠܓܗ"
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = " ܪܘܒܥܐ ܩܐ" + pronounce_number_syr(next_hour)
        else:
            speak = pronounce_number_syr(hour)

            if dt.minute == 0:
                if not use_ampm:
                    return speak
            else:
                speak += " ܘ " + pronounce_number_syr(dt.minute) + ' ܩܛܝܢ̈ܬ̣ܐ'

        if use_ampm:
            if dt.hour > 11:
                speak += " ܒܬܪ ܛܗܪܝܐ"
            else:
                speak += " ܩܕܡ ܛܗܪܐ"

        return speak
