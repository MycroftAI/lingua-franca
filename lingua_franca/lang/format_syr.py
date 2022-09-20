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
    _SYRIAC_ORDINAL_BASE, _SYRIAC_SEPARATOR, \
    _SYRIAC_CONJOINER, _SYRIAC_FRAC, _SYRIAC_FRAC_BIG
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

    ### For text

    if not speech:
        if num == 0:
            # TODO: Number grouping?  E.g. "1,000,000"
            return str(whole)
        else:
            return_string = '{} {}/{}'.format(whole, num, den)
            return return_string

    ### For speech

    # If the number is not a fraction, return the whole number
    if num == 0:
        return str(whole)

    #print(f'number: {number} - whole {whole}, numerator {num}, denominator {den}')

    # If the whole number is 0
    if whole == 0:
        # Special case for half for 0.5
        if num == 1 and den == 2:
            return_string = 'ܦܠܓܐ'
            #print(f'return-ܦܠܓܐ {return_string}')
        else:
            # 
            return_string = '{} ܡܢ {}'.format(_lookup_syriac_word(num), _lookup_syriac_word(den))
            #print(f'return-1 {return_string}')
    # If the whole number is > 0        
    elif num == 1 and den == 2:
        # Special case for half for whole numbers with 0.5
        return_string = '{} ܘܦܠܓܐ'.format(whole)
        #print(f'return-2 {return_string}')
    else:
        return_string = '{} ܘ{} ܡܢ {}'.format(whole, _lookup_syriac_word(num), _lookup_syriac_word(den))
        #print(f'return-3 {return_string}')
    return return_string

def _unpack_number_to_parts(value, _precision):
    """
    Given a number, break it down to its whole number and fractional number parts

    Returns:
        (pre): The whole number
        (post): The fractional number
        (_precision): The precision
    """
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

    #print(f'_unpack_number_to_parts {value}: pre {pre}, post {post}, precision {_precision}')
    return pre, post, _precision

def _lookup_syriac_word(number, ordinals=False):
    """
    Lookup up the appropriate Syriac word given a number and then create a string based
    on the number range

    Args:
        num(float or int): the number to pronounce (under 100)
        ordinals (bool): pronounce in ordinal form "first" instead of "one"

    Returns: Number string    
    """
    if (number < 20):
        if ordinals:
            return _SYRIAC_ORDINAL_BASE[number]
        return _SYRIAC_ONES[number]

    if (number < 100):
        quotient, remainder = divmod(number, 10)
        if remainder == 0:
            if ordinals:
                return _SYRIAC_ORDINAL_BASE[number]
            return _SYRIAC_TENS[quotient] 
        if ordinals:
            #print(f'_lookup_syriac_word <100 // number {number}: quotient {quotient}, remainder {remainder}')
            return _SYRIAC_TENS[quotient] + _SYRIAC_CONJOINER + _SYRIAC_ORDINAL_BASE[remainder]
        return _SYRIAC_TENS[quotient] + _SYRIAC_CONJOINER + _SYRIAC_ONES[remainder]
    
    quotient, remainder = divmod(number, 100)
    
    if remainder == 0:
        if ordinals:
            #print(f'number is {number} = quotient {quotient}, remainder {remainder}')
            #print(f'number is {number} = ordinal is {_SYRIAC_ORDINAL_BASE[number]}')
            return _SYRIAC_ORDINAL_BASE[number]
        #print(f'hundreds is {_SYRIAC_HUNDREDS[x]}')
        return _SYRIAC_HUNDREDS[quotient]

    #print(f'_lookup_syriac_word >100 // number {number}: quotient {quotient}, remainder {remainder}')
    #if ordinals:
        #print(f'number is {number} = quotient {quotient}, remainder {remainder}')
        #print(f'number is {number} = ordinal is {_SYRIAC_ORDINAL_BASE[number]}')
        #_SYRIAC_HUNDREDS[quotient] + _SYRIAC_CONJOINER
    #    pass
    return _SYRIAC_HUNDREDS[quotient] + _SYRIAC_CONJOINER + _lookup_syriac_word(remainder)

def _generate_whole_numbers(number, ordinals=False):
    """
    Given a number, through subsequent passes of the _SYRIAC_LARGE list generate a number
    string for each pass and then generate a final string.

    For example, 103254654 will generate the following strings per each pass:

    pass [] ܫܬܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ, result ܫܬܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ
    pass [ܐܠܦܐ] ܬܪܝܢܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ ܐܠܦܐ, result ܬܪܝܢܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ ܐܠܦܐ ܘܫܬܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ
    pass [ܡܠܝܘܢܐ] ܡܐܐ ܘܬܠܬܐ ܡܠܝܘܢܐ, result ܡܐܐ ܘܬܠܬܐ ܡܠܝܘܢܐ ܘܬܪܝܢܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ ܐܠܦܐ ܘܫܬܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ

    Args:
        num(float or int): the number to pronounce (under 100)
        ordinals (bool): pronounce in ordinal form "first" instead of "one"

    Returns:
        (result): The final number string
    """
    temp_number = number
    result = ''

    for syriac_large_num in _SYRIAC_LARGE:
        temp_number, remainder = divmod(temp_number, 1000)
        if (remainder == 0):
            continue
        
        if ordinals:
            text = _lookup_syriac_word(number, ordinals)
            #print(f'_generate_whole_numbers // number {number}: quotient {temp_number}, remainder {remainder}, text {text}')
        else:
            text = _lookup_syriac_word(remainder)
        
        if not ordinals:
            if remainder == 1 and syriac_large_num == 'ܐܠܦܐ':
                    text = syriac_large_num
            elif syriac_large_num != '':
                if ordinals:
                    pass
                else:
                    text += ' ' + syriac_large_num

        if (result == ''):
            result = text
        else:
            result = text + _SYRIAC_CONJOINER + result
        #print(f'{number}: text {text}, remainder {remainder}, result {result}, syriac_large_num {syriac_large_num}')    
        #print(f'_generate_whole_numbers {number}: quotient {temp_number}, remainder {remainder}, syriac_string {syriac_string}, result {result}')
    return result

def _generate_fractional_numbers(number, _precision):
    """
    Given a number, generate the whole number string + fractional string

    Returns:
        (result): The final number string
    """
    if (number / 10**_precision == 0.5):
        return "ܦܠܓܐ"

    whole = _generate_whole_numbers(number)
    quotient, remainder = divmod(_precision, 3)
    #print(f'_generate_fractional_numbers {number}: whole is {whole}, quotient is {quotient}, remainder is {remainder}')
    
    # String will either have part of the _SYRIAC_FRAC OR the _SYRIAC_FRAC_BIG list
    fractional = _SYRIAC_SEPARATOR + _SYRIAC_FRAC[remainder] + _SYRIAC_FRAC_BIG[quotient]
    
    result = whole + fractional
    return result

def _generate_numbers_string(number, places, ordinals=False):
    if number < 0:
        return "ܣܚܘܦܐ " + _generate_numbers_string(-number, places)
        #print(f'cardinal: {"ܣܚܘܦܐ " + _generate_numbers_string(-number, places)}')
    if (number == 0):
        return "ܣܝܦܪ"

    whole, fractional, precision = _unpack_number_to_parts(number, places)

    if fractional == 0:
        if ordinals:
            return _generate_whole_numbers(whole, ordinals)    
        else:
            return _generate_whole_numbers(whole)
    if whole == 0:
        return _generate_fractional_numbers(fractional, precision)

    
    result = _generate_whole_numbers(whole) + _SYRIAC_CONJOINER + _generate_fractional_numbers(fractional, precision)
    #print(f'cardinal_string {number}: {cardinal_string}')
    #print(f'_generate_whole_numbers {whole}: {_generate_whole_numbers(whole)}, _generate_fractional_numbers {fractional, precision}: {_generate_fractional_numbers(fractional, precision)}')      
    return result

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
        #print(f'numbers is {number}: n is {n}, power is {power}')
        if power != 0:
            return '{}{} ܥܦܝܦ ܥܣܪܐ ܒܚܝܠܐ ܕ{}{}'.format(
                'ܣܚܘܦܐ ' if float(n) < 0 else '',
                pronounce_number_syr(
                    abs(float(n)), places, False, ordinals=False),
                'ܣܚܘܦܐ ' if power < 0 else '',
                pronounce_number_syr(abs(power), places, False, ordinals=False))
    if ordinals:
        #print(f'number: {number} // ordinals: {_generate_ordinal_numbers(number)}')
        return _generate_numbers_string(number, places, ordinals=True)

    #print(f'number: {number} // ordinals: {_generate_numbers_string(number, places)}')    
    return _generate_numbers_string(number, places)
    
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
            speak += " ܘ"
            if string[3] == '0':
                speak += pronounce_number_syr(int(string[4]))
            else:
                speak += pronounce_number_syr(int(string[3:5]))
            speak += ' ܩܛܝܢ̈ܬܐ'
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
            speak = pronounce_number_syr(hour) + " ܘܦܠܓܐ"
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "ܪܘܒܥܐ ܩܐ " + pronounce_number_syr(next_hour)
        else:
            speak = pronounce_number_syr(hour)

            if dt.minute == 0:
                if not use_ampm:
                    return speak
            else:
                speak += " ܘ" + pronounce_number_syr(dt.minute) + ' ܩܛܝܢ̈ܬܐ'

        if use_ampm:
            if dt.hour > 11:
                speak += " ܒܬܪ ܛܗܪܐ"
            else:
                speak += " ܩܕܡ ܛܗܪܐ"

        return speak
