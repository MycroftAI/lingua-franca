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
from datetime import datetime, timedelta
# import locale

from lingua_franca.parse import normalize
# locale.setlocale(locale.LC_TIME, "fa_IR")
from dateutil.relativedelta import relativedelta

from lingua_franca.time import now_local
from lingua_franca.lang.parse_common import is_numeric, look_for_fractions, \
    invert_dict, ReplaceableNumber, partition_list, tokenize, Token, Normalizer
from lingua_franca.lang.common_data_fa import _FARSI_SUMS, _STRING_DECIMAL_FA, \
    _ORDINAL_FA, _NEGATIVES_FA, _DECIMAL_MARKER_FA, _STRING_NUM_FA, _STRING_SCALE_FA, \
    _STRING_ORDINAL_FA, _STRING_FRACTION_FA, _EXTRA_SPOKEN_NUM_FA

import re
import json
from lingua_franca.internal import resolve_resource_file


def _replace_farsi_numbers(text):
    for i in text:
        if ord(i) in range(1776, 1786):
            text = text.replace(i, chr(ord(i)-1728))
    return text

def _convert_words_to_numbers_fa(text, short_scale=True, ordinals=False):
    """
    Convert words in a string into their equivalent numbers.
    Args:
        text str:
        short_scale boolean: True if short scale numbers should be used.
        ordinals boolean: True if ordinals (e.g. یکم, دوم, سوم) should
                          be parsed to their number values (1, 2, 3...)

    Returns:
        str
        The original text, with numbers subbed in where appropriate.

    """
    tokens = tokenize(text)
    numbers_to_replace = \
        _extract_numbers_with_text_fa(tokens, short_scale, ordinals)
    numbers_to_replace.sort(key=lambda number: number.start_index)

    results = []
    for token in tokens:
        if not numbers_to_replace or \
                token.index < numbers_to_replace[0].start_index:
            results.append(token.word)
        else:
            if numbers_to_replace and \
                    token.index == numbers_to_replace[0].start_index:
                results.append(str(numbers_to_replace[0].value))
            if numbers_to_replace and \
                    token.index == numbers_to_replace[0].end_index:
                numbers_to_replace.pop(0)

    return ' '.join(results)

def _extract_numbers_with_text_fa(tokens, short_scale=True, ordinals=False, fractional_numbers=True):
    """
    Extract all numbers from a list of Tokens, with the words that
    represent them.

    Args:
        [Token]: The tokens to parse.
        short_scale bool: True if short scale numbers should be used, False for
                          long scale. True by default.
        ordinals bool: True if ordinal words (first, second, third, etc) should
                       be parsed.
        fractional_numbers bool: True if we should look for fractions and
                                 decimals.

    Returns:
        [ReplaceableNumber]: A list of tuples, each containing a number and a
                         string.

    """
    placeholder = "<placeholder>"  # inserted to maintain correct indices
    results = []
    while True:
        to_replace = \
            _extract_number_with_text_fa(tokens, short_scale,
                                         ordinals, fractional_numbers)

        if not to_replace:
            break

        results.append(to_replace)

        tokens = [
            t if not
            to_replace.start_index <= t.index <= to_replace.end_index
            else
            Token(placeholder, t.index) for t in tokens
        ]
    results.sort(key=lambda n: n.start_index)
    return results

def _extract_number_with_text_fa(tokens, short_scale=True, ordinals=False, fractional_numbers=True):
    """
    Handle numbers.

    Args:
        tokens [Token]:
        short_scale boolean:
        ordinals boolean:
        fractional_numbers boolean:

    Returns:
        ReplaceableNumber

    """

    number_words = [] 
    val = False
    state = 0
    num_state = 0
    to_sum = []
    negative = 1
    explicit_ordinals = False
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        idx += 1
        current_val = None
        
        word = token.word.lower()
        if ordinals and word in _STRING_ORDINAL_FA:
            word = str(_STRING_ORDINAL_FA[word])
            explicit_ordinals = True
        
        prev_word = tokens[idx - 1].word.lower() if idx > 0 else ""
        prevprev_word = tokens[idx - 2].word.lower() if idx > 1 else ""
        next_word = tokens[idx + 1].word.lower() if idx + 1 < len(tokens) else ""

        # explicit ordinals
        if is_numeric(word[:-2]) and \
                (word.endswith("ام")):
            word = word[:-2]
            explicit_ordinals = True
        if word in _STRING_NUM_FA:
            if ordinals and word not in _FARSI_SUMS:
                val = False
                continue
            word = _STRING_NUM_FA[word]
        if state == 0:
            if is_numeric(word):
                current_val = float(word)
                if ordinals and not explicit_ordinals and current_val < 20:
                    val = False
                    continue
                
                if num_state == 0:
                    number_words.append(token)
                    state = 1
                    val = current_val
                    if current_val < 20:
                        num_state = 1
                    elif current_val < 100 and current_val % 10 == 0:
                        num_state = 2
                    elif current_val < 1000 and current_val % 100 == 0:
                        num_state = 3
                    elif current_val < 1000 and current_val % 10 == 0:
                        num_state = 2
                    else:
                        num_state = 4
                elif num_state == 1:
                    break
                elif num_state == 2:
                    if 0 < current_val < 10:
                        val += current_val
                        num_state = 0
                        number_words.append(token)
                        state = 1
                    else:
                        to_sum.append(val)
                        val = False
                        state = 0
                        num_state = 0
                        idx -= 1
                elif num_state == 3:
                    if current_val < 100:
                        number_words.append(token)
                        state = 1
                        val += current_val
                        if current_val < 20:
                            num_state = 1
                        elif current_val % 10 == 0:
                            num_state = 2
                        else:
                            num_state = 1
                    else:
                        to_sum.append(val)
                        state = 0
                        num_state = 0
                        val = False
                        idx -= 1
                elif num_state == 4:
                    to_sum.append(val)
                    state = 0
                    num_state = 0
                    val = False
                    idx -= 1         
            elif '/' in word:
                temp = word.split('/')
                if len(temp) == 2:
                    current_val = int(temp[0]) / int(temp[1])
                    val = current_val
                    number_words.append(token)
            elif word in _EXTRA_SPOKEN_NUM_FA:
                current_val =  1 / _EXTRA_SPOKEN_NUM_FA[word]
                if not val:
                    val = 0
                val += current_val
                number_words.append(token)
                state = 1
                num_state = 1
            elif word in _NEGATIVES_FA:
                negative = -1
                number_words.append(token)
                val = False
                state = 0
                num_state = 0
            elif word == 'و':
                number_words.append(token)
                continue
            else:
                if not val and not to_sum:
                    continue
                else:
                    break
        elif state == 1:
            if word == 'و':
                number_words.append(token)
                current_val = False
                state = 0
                if num_state == 0:
                    to_sum.append(val)
                    val = False
            elif word == 'ممیز':
                number_words.append(token)
                current_val = False
                to_sum.append(val)
                temp = _extract_number_with_text_fa(tokens[idx:], short_scale, ordinals, fractional_numbers)
                degree = 1
                while temp.value > 10 ** degree:
                    degree += 1
                to_sum.append(temp.value / 10 ** degree)
                for t in temp.tokens:
                    number_words.append(t)
                val = False
                break
            elif word in _STRING_SCALE_FA:
                current_val = _STRING_SCALE_FA[word]
                val *= current_val
                to_sum.append(val)
                val = False
                number_words.append(token)
                state = 0
                num_state = 0
            elif word == 1000:
                current_val = word
                val *= current_val
                to_sum.append(val)
                val = False
                number_words.append(token)
                state = 0
                num_state = 0
            elif word in _STRING_DECIMAL_FA:
                current_val = 10 ** _STRING_DECIMAL_FA[word]
                val /= current_val
                to_sum.append(val)
                val = False
                number_words.append(token)
                state = 0
            elif word in _STRING_FRACTION_FA:
                current_val = _STRING_FRACTION_FA[word]
                val /= current_val
                to_sum.append(val)
                val = False
                number_words.append(token)
                state = 0
            else:
                break

    if to_sum:
        val += sum(to_sum)
    if val is not False:
        val = negative * val
    if val and val % 1 == 0:
        val = int(val)
    return ReplaceableNumber(val, number_words)
    # return ReplaceableNumber(False, [])

def extract_numbers_fa(text, short_scale=True, ordinals=False):
    """
        Takes in a string and extracts a list of numbers.

    Args:
        text (str): the string to extract a number from
        short_scale (bool): Use "short scale" or "long scale"
        ordinals (bool): consider ordinal numbers
    Returns:
        list: list of extracted numbers as floats
    """
    text = _replace_farsi_numbers(text)
    normalizer = FarsiNormalizer()
    text = normalizer.replace_words(text)
    text = normalizer.normalize_ordinals(text)
    results = _extract_numbers_with_text_fa(tokenize(text),
                                            short_scale, ordinals)
    return [float(result.value) for result in results]

def extract_number_fa(text, short_scale=True, ordinals=False):
    """
    This function extracts a number from a text string

    https://en.wikipedia.org/wiki/Names_of_large_numbers

    Args:
        text (str): the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers
    Returns:
        (int) or (float) or False: The extracted number or False if no number
                                   was found

    """
    text = _replace_farsi_numbers(text)
    text = FarsiNormalizer().replace_words(text)
    return _extract_number_with_text_fa(tokenize(text.lower()),
                                        short_scale, ordinals).value

def extract_duration_fa(text):
    """
    Convert an english phrase into a number of seconds

    Convert things like:
        "۱۰ دقیقه"
        "۲ و نیم ساعت"
        "۳ روز و ۸ساعت و ۱۰ دقیقه و ۴۹ ثانیه"
    into an int, representing the total number of seconds.

    The words used in the duration will be consumed, and
    the remainder returned.

    As an example, "برای ۵ دقیقه هشدار تنظیم کن" would return
    (300, "برای  هشدار تنظیم کن").

    Args:
        text (str): string containing a duration

    Returns:
        (timedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.
    """
    if not text:
        return None

    time_units = {
        'microseconds': 0,
        'milliseconds': 0,
        'seconds': 0,
        'minutes': 0,
        'hours': 0,
        'days': 0,
        'weeks': 0
    }

    time_units_fa = {
        'میکرو ثانیه': 'microseconds',
        'میلی ثانیه': 'milliseconds',
        'ثانیه': 'seconds',
        'دقیقه': 'minutes',
        'ساعت': 'hours',
        'روز': 'days',
        'هفته': 'weeks'
    }

    # pattern = r"(?P<value>\d+(?:\.?\d+)?)(?:\s+|\-){unit}?"
    pattern = r"(?P<value>\d+(?:\.?\d+)?)(?:\s+|\-){unit}?(?:(?:\s|,|و)+)?(?P<half>نیم|0\.5)?"
    text = _convert_words_to_numbers_fa(text)
    print(text)
    for unit_fa in time_units_fa:
        unit_pattern = pattern.format(unit=unit_fa)

        def repl(match):
            time_units[time_units_fa[unit_fa]] += float(match.group(1))
            return ''
        text = re.sub(unit_pattern, repl, text)

    text = text.strip()
    duration = timedelta(**time_units) if any(time_units.values()) else None

    return (duration, text)

def extract_datetime_fa(text, anchorDate=None, default_time=None):
    """ Convert a human date reference into an exact datetime

    Convert things like
        "امروز"
        "فردا بعد از ظهر"
        "سه شنبه بعد ساعت 4 بعد از ظهر"
        "سوم آگوست"
    into a datetime.  If a reference date is not provided, the current
    local time is used.  Also consumes the words used to define the date
    returning the remaining string.  For example, the string
       "سه شنبه هوا چطوره؟"
    returns the date for the forthcoming Tuesday relative to the reference
    date and the remainder string
       "هوا چطوره".

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
    def clean_string(s):
        # normalize and lowercase utt  (replaces words with numbers)
        s = _convert_words_to_numbers_fa(s, ordinals=True)
        # clean unneeded punctuation and capitalization among other things.
        s = s.lower().replace('?', '').replace(',', '').replace('؟', '')

        wordList = s.split()
        skip_next_word = False
        skip_next_next_word = False
        new_words = []
        for idx, word in enumerate(wordList):
            if skip_next_word:
                if not skip_next_next_word:
                    skip_next_word = False
                skip_next_next_word = False
                continue
            wordNext     = wordList[idx + 1] if idx + 1 < len(wordList) else ""
            wordNextNext = wordList[idx + 2] if idx + 2 < len(wordList) else ""

            ordinals = ["ام"]
            if word[0].isdigit():
                for ordinal in ordinals:
                    if wordNext.startswith(ordinal):
                        skip_next_word = True
            if (word in ['بعد', 'قبل'] and wordNext == 'از' and wordNextNext == 'ظهر'):
                word = word + ' ' + wordNext + ' ' + wordNextNext
                skip_next_word = True
                skip_next_next_word = True
            if (word in ['یک', 'سه', 'دو', 'پنج'] and wordNext == 'شنبه')\
               or (word in ['نیمه', 'نصف'] and wordNext == 'شب'):
                word = word + wordNext
                skip_next_word = True
            new_words.append(word)
        return new_words

    def date_found():
        return found or \
            (
                datestr != "" or
                yearOffset != 0 or monthOffset != 0 or
                dayOffset is True or hrOffset != 0 or
                hrAbs or minOffset != 0 or
                minAbs or secOffset != 0
            )

    if not anchorDate:
        anchorDate = now_local()

    if text == "":
        return None

    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    today = anchorDate.strftime("%w")
    currentYear = anchorDate.strftime("%Y")
    datestr = ""
    hasYear = False
    timeQualifier = ""

    timeQualifiersAM = ['صبح', 'قبل از ظهر', 'بامداد']
    timeQualifiersPM = ['بعد از ظهر', 'عصر', 'شب', 'امشب']
    timeQualifiersList = set(timeQualifiersAM + timeQualifiersPM)
    markers = ['نیم', 'در', 'عرض', 'برای', 'از', 'این']
    days = ['دوشنبه', 'سهشنبه', 'چهارشنبه',
            'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
    months = ['ژانویه', 'فوریه', 'مارس', 'آوریل', 'می', 'ژوئن',
              'ژوئیه', 'اوت', 'سپتامبر', 'اکتبر', 'نوامبر',
              'دسامبر']
    eng_months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november',
                  'december']
    recur_markers = days + [d + ' ها' for d in days]
    year_multiples = ["دهه", "قرن", "هزاره"]
    day_multiples = ["هفته", "ماه", "سال"]
    text = _convert_words_to_numbers_fa(text)
    words = clean_string(text)
    print(words)
    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrevPrev = words[idx - 3] if idx > 2 else ""  
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""

        # this isn't in clean string because I don't want to save back to words
        start = idx
        used = 0
        # save timequalifier for later
        if word == "الان" and not datestr:
            resultStr = " ".join(words[idx + 1:])
            resultStr = ' '.join(resultStr.split())
            extractedDate = anchorDate.replace(microsecond=0)
            return [extractedDate, resultStr]
        elif wordNext in year_multiples:
            multiplier = None
            if is_numeric(word):
                multiplier = extract_number_fa(word)
            multiplier = multiplier or 1
            multiplier = int(multiplier)
            used += 2
            if wordNext == "دهه":
                yearOffset = multiplier * 10
            elif wordNext == "قرن":
                yearOffset = multiplier * 100
            elif wordNext == "هزاره":
                yearOffset = multiplier * 1000
        elif word in timeQualifiersList:
            timeQualifier = word
        # parse امروز, فردا, پسفردا
        elif word == "امروز":
            dayOffset = 0
            used += 1
        elif word == "فردا":
            dayOffset = 1
            used += 1
        elif word == "پریروز":
            dayOffset = -2
            used += 1
        elif word == "دیروز":
            dayOffset = -1
            used += 1
        elif word == "پسفردا":
            dayOffset = 2
            used = 1
        # parse 5 days, 10 weeks, last week, next week
        elif word == "روز":
            if wordPrev and wordPrev[0].isdigit():
                dayOffset += int(wordPrev)
                start -= 1
                used = 2
            elif wordNext:
                dayOffset = 1
                used = 1
            if wordNext == "بعد":
                used += 1
            elif wordPrevPrev == 'بعد':
                start -= 1
                used += 1
            elif wordNext in ["قبل", "پیش"]:
                dayOffset *= -1
                used += 1
        elif word == "هفته":
            if wordPrev and wordPrev[0].isdigit():
                dayOffset += int(wordPrev) * 7
                start -= 1
                used = 2
            elif wordNext:
                dayOffset = 7
                used = 1
            if wordPrevPrev == 'از' and wordPrevPrevPrev == 'بعد':
                start -= 2
                used += 2
            elif wordPrevPrev == 'بعد':
                start -= 1
                used += 1
            elif wordNext == "بعد":
                used += 1
            elif wordNext in ["قبل", "پیش"]:
                dayOffset *= -1
                used += 1
        # parse 10 months, next month, last month
        elif word == "ماه":
            if wordPrev and wordPrev[0].isdigit():
                monthOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordNext:
                monthOffset = 1
                used = 1
            if wordNext == "بعد":
                used += 1
            elif wordPrevPrev == 'بعد':
                start -= 1
                used += 1
            elif wordNext in ["قبل", "پیش"]:
                monthOffset *= -1
                used += 1
        # parse 5 years, next year, last year
        elif word == "سال":
            if wordPrev and wordPrev[0].isdigit():
                yearOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordNext:
                used = 1
                yearOffset = 1
            if wordNext == "بعد":
                used += 1
            elif wordPrevPrev == 'بعد':
                start -= 1
                used += 1
            elif wordNext in ["قبل", "پیش"]:
                yearOffset *= -1
                used += 1
        elif word == "دهه":
            if wordPrev and wordPrev[0].isdigit():
                yearOffset = int(wordPrev) * 10
                start -= 1
                used = 2
            elif wordNext:
                used = 1
                yearOffset = 10
            if wordNext == "بعد":
                used += 1
            elif wordPrevPrev == 'بعد':
                start -= 1
                used += 1
            elif wordNext in ["قبل", "پیش"]:
                yearOffset *= -1
                used += 1
        # parse Monday, Tuesday, etc., and next Monday,
        # last Tuesday, etc.
        elif word in days:
            d = days.index(word)
            dayOffset = (d + 1) - int(today)
            used = 1
            if dayOffset < 0:
                dayOffset += 7
            if wordNext == "بعد":
                if dayOffset <= 2:
                    dayOffset += 7
                used += 1
            elif wordNext == "قبل":
                dayOffset -= 7
                used += 1
            if wordPrev in markers:
                words[idx - 1] = ""
        # parse 15 of July, June 20th, Feb 18, 19 of February
        elif word in months:
            m = months.index(word)
            used += 1
            datestr = eng_months[m]
            if wordPrev and wordPrev[0].isdigit():
                datestr += " " + wordPrev
                start -= 1
                used += 1
                if wordNext and wordNext[0].isdigit():
                    datestr += " " + wordNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordNext and wordNext[0].isdigit():
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False
            else:
                datestr = ""
                used = 0

        if used > 0:
            if start - 1 > 0 and words[start - 1] == "این":
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in markers:
                words[start - 1] = ""
            found = True
            daySpecified = True

    # parse time
    hrOffset = 0
    minOffset = 0
    secOffset = 0
    hrAbs = None
    minAbs = None
    military = False

    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""    
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word == "ظهر":
            hrAbs = 12
            used += 1
        elif word in ["نصفشب", "نیمهشب"]:
            hrAbs = 0
            used += 1
        elif word == "صبح":
            if hrAbs is None:
                hrAbs = 8
            used += 1
        elif word == "بعد از ظهر":
            if hrAbs is None:
                hrAbs = 15
            used += 1
        elif word == "عصر":
            if hrAbs is None:
                hrAbs = 19
            used += 1

        # parse half an hour, quarter hour
        elif word == "ساعت" and wordPrev in markers:
            if wordPrev == "نیم":
                minOffset = 30
                used += 1
            else:
                hrOffset = 1
                used += 1
            words[idx - 1] = ""
            hrAbs = -1
            minAbs = -1       
        elif word[0].isdigit():
            isTime = True
            strHH = ""
            strMM = ""
            remainder = ""
            wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""
            if wordNext == "امشب" or wordNextNext == "امشب" or \
                    wordPrev == "امشب" or wordPrevPrev == "امشب":
                remainder = "شب"
                if wordPrev == "امشب":
                    words[idx - 1] = ""
                if wordPrevPrev == "امشب":
                    words[idx - 2] = ""
                if wordNextNext == "امشب":
                    used += 1
                if wordNextNextNext == "امشب":
                    used += 1

            if ':' in word:
                # parse colons
                # "3:00 in the morning"
                stage = 0
                length = len(word)
                for i in range(length):
                    if stage == 0:
                        if word[i].isdigit():
                            strHH += word[i]
                        elif word[i] == ":":
                            stage = 1
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 1:
                        if word[i].isdigit():
                            strMM += word[i]
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 2:
                        remainder = word[i:].replace(".", "")
                        break
                if remainder == "":
                    nextWord = wordNext.replace(".", "")
                    if nextWord == "صبح" or nextWord == "شب":
                        remainder = nextWord
                        used += 1

                    elif wordNext == "صبح":
                        remainder = "صبح"
                        used += 1
                    elif wordNext == "بعد از ظهر":
                        remainder = "شب"
                        used += 1
                    elif wordNext == "عصر":
                        remainder = "شب"
                        used += 1
                    elif wordNext == "امروز" and wordNextNext == "صبح":
                        remainder = "صبح"
                        used = 2
                        daySpecified = True
                    elif wordNext == "امروز" and wordNextNext == "بعد از ظهر":
                        remainder = "شب"
                        used = 2
                        daySpecified = True
                    elif wordNext == "امروز" and wordNextNext == "عصر":
                        remainder = "شب"
                        used = 2
                        daySpecified = True
                    else:
                        if timeQualifier != "":
                            military = True
                            if strHH and int(strHH) <= 12 and \
                                    (timeQualifier in timeQualifiersPM):
                                strHH += str(int(strHH) + 12)
                if wordPrev == 'ساعت' or wordPrev in markers:
                    words[idx - 1] = ''
                if wordPrevPrev in markers:
                    words[idx - 2] = ''
            else:
                length = len(word)
                strNum = ""
                for i in range(length):
                    if word[i].isdigit():
                        strNum += word[i]
                    else:
                        remainder += word[i]
                if remainder == "":
                    remainder = wordNext
                if remainder in timeQualifiersPM:
                    strHH = strNum
                    remainder = "شب"
                    used += 1
                elif remainder in timeQualifiersAM:
                    strHH = strNum
                    remainder = "صبح"
                    used += 1
                if (
                        remainder in recur_markers or
                        wordNext in recur_markers or
                        wordNextNext in recur_markers):
                    # Ex: "7 on mondays" or "3 this friday"
                    # Set strHH so that isTime == True
                    # when am or pm is not specified
                    strHH = strNum
                    used = 1
                else:
                    if wordNext == "ساعت" or remainder == "ساعت":
                        if is_numeric(word):
                            temp = float(word)
                            if temp < 1:
                                minOffset = int(temp * 60)
                                temp = 0
                            else:
                                temp = int(temp)
                        else:
                            temp = int(strNum)
                        hrOffset = temp
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                        print(wordPrev)
                        if wordPrev in markers:
                            words[idx - 1] = ''
                        if wordPrev in ['بعد', 'پس']:
                            words[idx - 1] = ''
                        if wordNextNext in ['دیگه', 'بعد']:
                            used += 1
                    elif wordNext == "دقیقه" or remainder == "دقیقه":
                        # "in 10 minutes"
                        minOffset = int(strNum)
                        print(minOffset)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                        if wordPrev in ['بعد', 'پس']:
                            words[idx - 1] = ''
                        if wordNextNext in ['دیگه', 'بعد']:
                            used += 1
                    elif wordNext == "ثانیه" or remainder == "ثانیه":
                        # in 5 seconds
                        secOffset = int(strNum)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1  
                        if wordPrev in ['بعد', 'پس']:
                            words[idx - 1] = ''
                        if wordNextNext in ['دیگه', 'بعد']:
                            used += 1              
                    elif wordPrev == 'ساعت':
                        strHH = strNum
                        words[idx - 1] = ''
                        if wordNext and wordNext[0].isdigit():
                            strMM = wordNext
                            used += 1
                            if wordNextNext == 'دقیقه':
                                used += 1
                    elif int(strNum) > 100:
                        strHH = str(int(strNum) // 100)
                        strMM = str(int(strNum) % 100)
                        military = True
                        if wordNext == "دقیقه":
                            used += 1
                        if wordPrev == "ساعت":
                            words[idx - 1] = ''
                    elif strHH:
                        pass
                    else:
                        isTime = False
                if wordPrev in markers:
                    words[idx - 1] = ""
                if wordPrevPrev in markers:
                    words[idx - 2] = ""
            HH = int(strHH) if strHH else 0
            MM = int(strMM) if strMM else 0
            HH = HH + 12 if remainder == "شب" and HH < 12 else HH
            HH = HH - 12 if remainder == "صبح" and HH >= 12 else HH

            if timeQualifier in timeQualifiersPM and HH < 12:
                HH += 12

            if HH > 24 or MM > 59:
                isTime = False
                used = 0
            if isTime:
                hrAbs = HH
                minAbs = MM
                used += 1

        if used > 0:
            # removed parsed words from the sentence
            for i in range(used):
                if idx + i >= len(words):
                    break
                words[idx + i] = ""

            idx += used - 1
            found = True
    # check that we found a date
    if not date_found():
        return None

    if dayOffset is False:
        dayOffset = 0

    # perform date manipulation

    extractedDate = anchorDate.replace(microsecond=0)

    if datestr != "":
        # date included an explicit date, e.g. "june 5" or "june 2, 2017"
        try:
            temp = datetime.strptime(datestr, "%B %d")
        except ValueError:
            # Try again, allowing the year
            temp = datetime.strptime(datestr, "%B %d %Y")
        extractedDate = extractedDate.replace(hour=0, minute=0, second=0)
        if not hasYear:
            temp = temp.replace(year=extractedDate.year,
                                tzinfo=extractedDate.tzinfo)
            if extractedDate < temp:
                extractedDate = extractedDate.replace(
                    year=int(currentYear),
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")),
                    tzinfo=extractedDate.tzinfo)
            else:
                extractedDate = extractedDate.replace(
                    year=int(currentYear) + 1,
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")),
                    tzinfo=extractedDate.tzinfo)
        else:
            extractedDate = extractedDate.replace(
                year=int(temp.strftime("%Y")),
                month=int(temp.strftime("%m")),
                day=int(temp.strftime("%d")),
                tzinfo=extractedDate.tzinfo)
    else:
        # ignore the current HH:MM:SS if relative using days or greater
        if hrOffset == 0 and minOffset == 0 and secOffset == 0:
            extractedDate = extractedDate.replace(hour=0, minute=0, second=0)

    if yearOffset != 0:
        extractedDate = extractedDate + relativedelta(years=yearOffset)
    if monthOffset != 0:
        extractedDate = extractedDate + relativedelta(months=monthOffset)
    if dayOffset != 0:
        extractedDate = extractedDate + relativedelta(days=dayOffset)
    if hrAbs != -1 and minAbs != -1:
        # If no time was supplied in the string set the time to default
        # time if it's available
        if hrAbs is None and minAbs is None and default_time is not None:
            hrAbs, minAbs = default_time.hour, default_time.minute
        else:
            hrAbs = hrAbs or 0
            minAbs = minAbs or 0

        extractedDate = extractedDate + relativedelta(hours=hrAbs,
                                                      minutes=minAbs)
        if (hrAbs != 0 or minAbs != 0) and datestr == "":
            if not daySpecified and anchorDate > extractedDate:
                extractedDate = extractedDate + relativedelta(days=1)
    if hrOffset != 0:
        extractedDate = extractedDate + relativedelta(hours=hrOffset)
    if minOffset != 0:
        extractedDate = extractedDate + relativedelta(minutes=minOffset)
    if secOffset != 0:
        extractedDate = extractedDate + relativedelta(seconds=secOffset)
    for idx, word in enumerate(words):
        if words[idx] == "and" and \
                words[idx - 1] == "" and words[idx + 1] == "":
            words[idx] = ""

    resultStr = " ".join(words)
    resultStr = ' '.join(resultStr.split())
    return [extractedDate, resultStr]

def is_fractional_fa(input_str, short_scale=True, spoken=True):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
        spoken (bool): consider "half", "quarter", "whole" a fraction
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """

    fracts = {"whole": 1, "half": 2, "halve": 2, "quarter": 4}
    for num in _ORDINAL_FA:
        if num > 2:
            fracts[_ORDINAL_FA[num]] = num

    if input_str.lower() in fracts and spoken:
        return 1.0 / fracts[input_str.lower()]
    return False

class FarsiNormalizer(Normalizer):
    with open(resolve_resource_file("text/fa-ir/normalize.json")) as f:
        _default_config = json.load(f)

    def numbers_to_digits(self, utterance):
        return _convert_words_to_numbers_fa(utterance, ordinals=None)

    def normalize_ordinals(self, text):
        words = self.tokenize(text)
        for idx, w in enumerate(words):
            for ordinal in _STRING_ORDINAL_FA:
                if w.startswith(ordinal):
                    words[idx] = ordinal
        utterance = " ".join(words)
        return utterance

def normalize_fa(text, remove_articles=True):
    """ Farsi string normalization """
    normalizer = FarsiNormalizer()
    text = normalizer.normalize_ordinals(text)
    return normalizer.normalize(text, remove_articles)
