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
import json
from datetime import timedelta

from lingua_franca.internal import resolve_resource_file
from lingua_franca.lang.common_data_syr import (_SYRIAC_ORDINAL_BASE, _SYRIAC_LARGE, 
                                                _SYRIAC_HUNDREDS, _SYRIAC_ONES, 
                                                _SYRIAC_TENS)
from lingua_franca.lang.parse_common import Normalizer
from lingua_franca.time import now_local


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def _parse_sentence(text):
    ar = text.split()
    result = []
    current_number = 0
    current_words = []
    s = 0
    step = 10
    mode = 'init'

    def finish_num():
        nonlocal current_number
        nonlocal s
        nonlocal result
        nonlocal mode
        nonlocal current_words
        current_number += s
        if current_number != 0:
            result.append((current_number, current_words))
        s = 0
        current_number = 0
        current_words = []
        mode = 'init'

    print(f'\nparse_sentence // {text}')
    for x in ar:
        print(f'parse_sentence // word: {x}')

        # Remove the first character, ܘ, from the word as it only signifies the word 'and'
        # with the rest of the word subsequent to it. Keep the original word in temp_word
        # so that we can append it to our current words
        #
        # x is used to lookup words in the lists
        # temp_word is used to append
        
        temp_word = x
        
        if x[0] == "ܘ":
            x = x[1:]
                     
        if x == "ܦܠܓܐ":                
            current_words.append(temp_word)
            current_number += 0.5
            finish_num()
        elif x in _SYRIAC_ONES:
            t = _SYRIAC_ONES.index(x)
            if mode != 'init' and mode != 'num_hundred' and mode != 'num':
                if not(t < 10 and mode == 'num_ten'):
                    finish_num()    
            current_words.append(temp_word)
            s += t
            mode = 'num_one'
        elif x in _SYRIAC_TENS:
            if mode != 'init' and mode != 'num_hundred' and mode != 'num':
                finish_num()
            current_words.append(temp_word)
            s += _SYRIAC_TENS.index(x)*10
            mode = 'num_ten'
        elif x in _SYRIAC_HUNDREDS:
            if mode != 'init' and mode != 'num':
                finish_num()
            current_words.append(temp_word)
            s += _SYRIAC_HUNDREDS.index(x)*100
            mode = 'num_hundred'
        elif x in _SYRIAC_LARGE:
            current_words.append(temp_word)
            d = _SYRIAC_LARGE.index(x)
            if mode == 'init' and d == 1:
                s = 1
            s *= 10**(3*d)            
            current_number += s
            s = 0
            mode = 'num'
        elif x in list(_SYRIAC_ORDINAL_BASE.values()):
            current_words.append(temp_word)
            s = list(_SYRIAC_ORDINAL_BASE.values()).index(x)
            current_number = s
            s = 1
            mode = 'num'
        elif _is_number(x):
            current_words.append(temp_word)
            current_number = float(x)
            finish_num()
        else:
            finish_num()
            result.append(x)            
    if mode[:3] == 'num':
        finish_num()   
    return result


_time_units = {
    'ܪ̈ܦܦܐ': timedelta(seconds=1),
    'ܪܦܦܐ': timedelta(seconds=1),
    'ܩܛܝܢ̈ܬܐ': timedelta(minutes=1),
    'ܩܛܝܢܬܐ': timedelta(minutes=1),
    'ܩܛܝܢ̈ܐ': timedelta(minutes=1),
    'ܩܛܝܢܐ': timedelta(minutes=1),
    'ܕܩܝܩ̈ܬܐ': timedelta(minutes=1),
    'ܕܩܝܩܬܐ': timedelta(minutes=1),
    'ܕܩܝܩ̈ܐ': timedelta(minutes=1),
    'ܕܩܝܩܐ': timedelta(minutes=1),
    'ܫܥܬܐ': timedelta(hours=1),
    'ܫܥ̈ܐ': timedelta(hours=1),
    'ܣܥܬ': timedelta(hours=1),
    'ܣܥܬ̈ܐ': timedelta(hours=1),
}

_date_units = {
    'ܝܘܡܢ̈ܐ': timedelta(days=1),
    'ܝܘܡܐ': timedelta(days=1),
    'ܫܒ̈ܘܥܐ': timedelta(weeks=1),
    'ܫܒܘܥܐ': timedelta(weeks=1),
    'ܫܒ̈ܬܐ': timedelta(weeks=1),
    'ܫܒܬܐ': timedelta(weeks=1),
}

def extract_duration_syr(text):
    """
    Convert an english phrase into a number of seconds

    Convert things like:
        "10 minute"
        "2 and a half hours"
        "3 days 8 hours 10 minutes and 49 seconds"
    into an int, representing the total number of seconds.

    The words used in the duration will be consumed, and
    the remainder returned.

    As an example, "set a timer for 5 minutes" would return
    (300, "set a timer for").

    Args:
        text (str): string containing a duration

    Returns:
        (timedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.
    """
    remainder = []
    ar = _parse_sentence(text)
    current_number = None
    result = timedelta(0)
    for x in ar:
        print(f'extract_duration: sentence: {ar}, x {x}')
        if x[0] == "ܘ":
            # Remove the first character, ܘ, from the word as it only signifies the word 'and'
            # with the rest of the word subsequent
            #
            # x is used to lookup words in the lists
            # temp_word is used to append
        
            temp_word = x
            x = x[1:]

        if type(x) == tuple:
            print(f'extract_duration: sentence: {ar}, x is tuple, word {x}')
            current_number = x
        elif x in _time_units:
            print(f'extract_duration: time_unit: {x}, current_number {current_number[0]}')
            result += _time_units[x] * current_number[0]
            current_number = None
        elif x in _date_units:
            print(f'extract_duration: date_unit: {x}, and current_number {current_number[0]}')            
            result += _date_units[x] * current_number[0]
            current_number = None
        else:
            #print(f'other: {x}')
            #print(f'current number: {current_number}')
            if current_number:
                remainder.extend(current_number[1])
            #print(f'remainder: {remainder}')
            remainder.append(x)
            current_number = None
    return (result, " ".join(remainder))


def extract_datetime_syr(text, anchorDate=None, default_time=None):
    """ Convert a human date reference into an exact datetime

    Convert things like
        "today"
        "tomorrow afternoon"
        "next Tuesday at 4pm"
        "August 3rd"
    into a datetime.  If a reference date is not provided, the current
    local time is used.  Also consumes the words used to define the date
    returning the remaining string.  For example, the string
       "what is Tuesday's weather forecast"
    returns the date for the forthcoming Tuesday relative to the reference
    date and the remainder string
       "what is weather forecast".

    The "next" instance of a day or weekend is considered to be no earlier than
    48 hours in the future. On Friday, "next Monday" would be in 3 days.
    On Saturday, "next Monday" would be in 9 days.

    Args:
        text (str): string containing date words
        anchorDate (datetime): A reference date/time for "tommorrow", etc
        default_time (time): Time to set if no time was found in the string

    Returns:
        [datetime, str]: An array containing the datetime and the remaining
                         text not consumed in the parsing, or None if no
                         date or time related text was found.
    """
    if text == "":
        print(f'extract_datetime // NO TEXT')
        return None
    text = text.lower().replace('‌', ' ').replace('.', '').replace('،', '') \
        .replace('?', '') \
        .replace('ܬܪܝܢ ܒܫܒܐ', 'ܬܪܝܢܒܫܒܐ') \
        .replace('ܬܠܬܐ ܒܫܒܐ', 'ܬܠܬܒܫܒܐ') \
        .replace('ܐܪܒܥܐ ܒܫܒܐ', 'ܐܪܒܥܒܫܒܐ') \
        .replace('ܚܡܫܐ ܒܫܒܐ', 'ܚܡܫܒܫܒܐ') \
        .replace('ܚܕ ܒܫܒܐ', 'ܚܕܒܫܒܐ') \
        
        
    if not anchorDate:
        anchorDate = now_local()

    today = anchorDate.replace(hour=0, minute=0, second=0, microsecond=0)
    today_weekday = int(anchorDate.strftime("%w"))
    weekday_names = [
        'ܬܪܝܢܒܫܒܐ',
        'ܬܠܬܒܫܒܐ',
        'ܐܪܒܥܒܫܒܐ',
        'ܚܡܫܒܫܒܐ',
        'ܥܪܘܒܬܐ',
        'ܫܒܬܐ',
        'ܚܕܒܫܒܐ',
    ]
    daysDict = {
        'ܬܡܠ': today + timedelta(days= -2),
        'ܬܡܠ': today + timedelta(days= -1),
        'ܐܕܝܘܡ': today,
        'ܝܘܡܐ ܕܐܬܐ': today + timedelta(days= 1),
        'ܝܘܡܐ ܐܚܪܢܐ': today + timedelta(days= 2),
    }
    timesDict = {
        'ܩܕܡ ܛܗܪܐ': timedelta(hours=8),
        'ܒܬܪ ܛܗܪܐ': timedelta(hours=15),
    }
    exactDict = {
        'ܗܫܐ': anchorDate,
    }
    nextWords = ["ܒܬܪ", "ܡܢ ܒܬܪ", "ܒܬܪ ܗܕܐ", "ܒܬܪܝܐ"]
    prevWords = ["ܩܕܝܡܐܝܬ", "ܡܩܕܡ ܕ", "ܩܕܡ", "ܡܢ ܩܕܡ", "ܩܘܕܡܐܝܬ", "ܩܕܡ ܐܕܝܐ"]
    ar = _parse_sentence(text)
    mode = 'none'
    number_seen = None
    delta_seen = timedelta(0)
    remainder = []
    result = None
    for x in ar:
        print(f'extract_datetime // word {x}')
        handled = 1
        if mode == 'finished':
            print(f'extract_datetime // mode is finished: remainder {x}')
            remainder.append(x)

        if x == 'ܘ' and mode[:5] == 'delta':
            print(f'extract_datetime // ܘ and mode = delta')
            pass
        
        if type(x) == tuple:
            print(f'extract_datetime // tuple {type(x)}, x is == {x}')
            number_seen = x
        elif x in weekday_names:
            dayOffset = (weekday_names.index(x) + 1) - today_weekday
            if dayOffset < 0:
                dayOffset += 7
            result = today + timedelta(days=dayOffset)
            mode = 'time'
        elif x in exactDict:
            result = exactDict[x]
            print(f'extract_datetime // exactDict {result}')
            mode = 'finished'
        elif x in daysDict:
            result = daysDict[x]
            print(f'extract_datetime // daysDict {result}')
            mode = 'time'
        elif x in timesDict and mode == 'time':
            result += timesDict[x]
            print(f'extract_datetime // timesDict {result}')    
            mode = 'finish'
        elif x in _date_units:
            print(f'extract_datetime // date_units {x}')
            k = 1
            if number_seen:
                k = number_seen[0]
                number_seen = None
            delta_seen += _date_units[x] * k
            if mode != 'delta_time':
                mode = 'delta_date'
        elif x in _time_units:
            print(f'extract_datetime // time_units {x}')
            k = 1
            #print(f'NUMBER SEEN: {number_seen[0]}')
            if number_seen:
                print(f'extract_datetime // number_seen = yes')
                k = number_seen[0]
                print(f'extract_datetime // number_seen {k}')
                number_seen = None
            delta_seen += _time_units[x] * k
            #print(f'extract_datetime // number_seen[0] {number_seen[0]}, _time_units {_time_units[x]}')
            print(f'extract_datetime // delta_seen {delta_seen}')
            mode = 'delta_time'
        elif x in nextWords or x in prevWords:
            # Give up instead of incorrect result
            print(f'extract_datetime // nextWords or prevWords {x} and mode {mode}')
            if mode == 'time':
                return None
            sign = 1 if x in nextWords else -1
        else:
            handled = 0

        if mode == 'delta_date':
            result = today + delta_seen
            mode = 'time'
        elif mode == 'delta_time':
            result = anchorDate + delta_seen
            mode = 'finished'
        else:
            handled = 0

        if handled == 1:
            continue

        if number_seen:
            remainder.extend(number_seen[1])
            number_seen = None
    
        #remainder.append(x)

    print(f'extract_datetime // result {result}, remainder {remainder}')    
    return (result, " ".join(remainder))

def extract_numbers_syr(text, short_scale=True, ordinals=False):
    """
        Takes in a string and extracts a list of numbers.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
    Returns:
        list: list of extracted numbers as floats
    """

    ar = _parse_sentence(text)    
    result = []
    for x in ar:
        print(f'extract_numbers_syr // x {x}')
        if type(x) == tuple:
            result.append(x[0])
    return result


def extract_number_syr(text, ordinals=False):
    """
    This function extracts a number from a text string,
    handles pronunciations in long scale and short scale

    https://en.wikipedia.org/wiki/Names_of_large_numbers

    Args:
        text (str): the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers, third=3 instead of 1/3
    Returns:
        (int) or (float) or False: The extracted number or False if no number
                                   was found

    """
    x = extract_numbers_syr(text, ordinals=ordinals)
    if (len(x) == 0):
        return False
    return x[0]
