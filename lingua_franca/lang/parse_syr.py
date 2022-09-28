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
                                                _SYRIAC_ONES_FEM, _SYRIAC_TENS, 
                                                _SYRIAC_FRACTIONS, _SYRIAC_FRACTIONS_HALF,
                                                _SYRIAC_SEPARATOR)
from lingua_franca.lang.parse_common import Normalizer
from lingua_franca.time import now_local

def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def _parse_sentence(text):
    words = text.split()
    result = []
    current_number = 0
    current_words = []
    sum_number = 0
    mode = 'init'

    def finish_num():
        nonlocal current_number
        nonlocal sum_number
        nonlocal result
        nonlocal mode
        nonlocal current_words
        current_number += sum_number
        if current_number != 0:
            result.append((current_number, current_words))
        sum_number = 0
        current_number = 0
        current_words = []
        mode = 'init'

    print(f'\nparse_sentence // word at top {text}')

    for word in words:
        print(f'parse_sentence // word is {word} // mode is {mode}')

        # Keep a copy of the word as we will modify it below
        temp_word = word

        # If the first letter starts with ܘ then treat it specifically as a conjoining ܘ as in this
        # context it is a conjoining letter and there is most likely a number following it
        if word[0] == "ܘ":
            word = word[1:] # Remove the ܘ to make the logic easier to follow 
            
            if mode == 'num_ten' or mode == 'num_hundred' or mode == 'num_one':
                print(f'parse_sentence // CONJOINER // word is {word} // mode is {mode}')
                mode += '_conjoiner'
            elif mode == 'num':
                print(f'parse_sentence // MODE NUM // word is {word} // mode is {mode}')
                pass
                #current_words.append(temp_word)
            else:
                print(f'parse_sentence // ELSE // word is {word} // mode is {mode}')
                finish_num()
                #result.append(temp_word)
        
        if word == "ܦܠܓܐ":
            print(f'parse_sentence // ܦܠܓܐ  // word is {word}')          
            current_words.append(temp_word)
            current_number += 0.5
            finish_num()        
        elif word in _SYRIAC_ONES or word in _SYRIAC_ONES_FEM:
            if word in _SYRIAC_ONES:
                temp_ones_number = _SYRIAC_ONES.index(word)
            elif word in _SYRIAC_ONES_FEM:
                temp_ones_number = _SYRIAC_ONES_FEM.index(word)
            print(f'parse_sentence // SYRIAC_ONES // {word}')
            if mode != 'init' and mode != 'num_hundred_conjoiner' and mode != 'num':
                if not(temp_ones_number < 10 and mode == 'num_ten_conjoiner'):
                    finish_num()    
            current_words.append(temp_word)
            sum_number += temp_ones_number
            mode = 'num_one'
            print(f'parse_sentence // SYRIAC_ONES // word {word} // mode {mode} // sum {sum_number}')
        elif word in _SYRIAC_TENS:
            if mode != 'init' and mode != 'num_hundred_conjoiner' and mode != 'num':
                finish_num()           
            current_words.append(temp_word)
            sum_number += _SYRIAC_TENS.index(word)*10
            mode = 'num_ten'
            print(f'parse_sentence // SYRIAC_TENS // word {word} // mode {mode} // sum {sum_number}')
        elif word in _SYRIAC_HUNDREDS:
            if mode != 'init' and mode != 'num':
                finish_num()
            current_words.append(temp_word)
            sum_number += _SYRIAC_HUNDREDS.index(word)*100
            mode = 'num_hundred'
        elif word in _SYRIAC_LARGE:
            current_words.append(temp_word)
            temp_large_number = _SYRIAC_LARGE.index(word)
            if mode == 'init' and temp_large_number == 1:
                sum_number = 1
            sum_number *= 10**(3*temp_large_number)            
            current_number += sum_number
            sum_number = 0
            mode = 'num'
        elif word in list(_SYRIAC_ORDINAL_BASE.values()):
            print(f'parse_sentence // SYRIAC_ORDINAL // {word}')
            current_words.append(temp_word)
            sum_number = list(_SYRIAC_ORDINAL_BASE.values()).index(word)
            current_number = sum_number
            sum_number = 1
            mode = 'num'
        elif _is_number(word):
            current_words.append(word)
            print(f'parse_sentence // SYRIAC_IS_NUMBER // {word}')
            current_number = float(word)
            finish_num()
        elif is_fractional_syr(word):
            print(f'parse_sentence // FRACTIONAL // {word}')
        else:
            finish_num()
            print(f'parse_sentence // ELSE down there // {word}')
            result.append(word)            
    if mode[:3] == 'num':
        finish_num()
    print(f'parse_sentence // RESULT // {result}')   
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
    words = _parse_sentence(text)
    current_number = None
    result = timedelta(0)
    for word in words:
        print(f'extract_duration: sentence: {words}, word is {word}')
        #if word[0] == "ܘ":
            # Remove the first character, ܘ, from the word as it only signifies the word 'and'
            # with the rest of the word subsequent
            #
            # word is used to lookup words in the lists
            # word_with_conjoiner is used to append
        
        #    temp_word = word
        #    word = word[1:]

        if type(word) == tuple:
            print(f'extract_duration: sentence: {words}, word is tuple, word {word}')
            current_number = word
        elif word in _time_units:
            print(f'extract_duration: time_unit: {word}, current_number {current_number[0]}')
            result += _time_units[word] * current_number[0]
            current_number = None
        elif word in _date_units:
            print(f'extract_duration: date_unit: {word}, and current_number {current_number[0]}')            
            result += _date_units[word] * current_number[0]
            current_number = None
        else:
            print(f'other: {word}')
            print(f'current number: {current_number}')
            if current_number:
                remainder.extend(current_number[1])
            print(f'remainder: {remainder}')
            remainder.append(word)
            current_number = None
    print(f'extract_duration // RESULT // {result} // REMAINDER // {remainder}')
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
        .replace('؟', '').replace("ܝܘܡܐ ܐܚܪܢܐ", "ܝܘܡܐܐܚܪܢܐ") \
        .replace('؟', '').replace("ܩܘܕܡܐ ܕܥܪܝܪܗ", "ܩܘܕܡܐܕܥܪܝܪܗ") \
        .replace('؟', '').replace("ܝܘܡܐ ܕܐܬܐ", "ܝܘܡܐܕܐܬܐ") \
        .replace('؟', '').replace("ܩܘܕܡܐ ܕܐܬܐ", "ܩܘܕܡܐܕܐܬܐ") \
        .replace('؟', '').replace("ܩܕܡ ܛܗܪܐ", "ܩܕܡܛܗܪܐ") \
        .replace('؟', '').replace("ܒܬܪ ܛܗܪܐ", "ܒܬܪܛܗܪܐ") \
        .replace('؟', '').replace("ܒܬܪ ܟܘܬܪܐ", "ܒܬܪܟܘܬܪܐ") \
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
        'ܩܘܕܡܐܕܥܪܝܪܗ': today + timedelta(days= -2),
        'ܬܡܠ': today + timedelta(days= -1),
        'ܐܕܝܘܡ': today,
        'ܝܘܡܐܕܐܬܐ': today + timedelta(days= 1),
        'ܩܘܕܡܐܕܐܬܐ': today + timedelta(days= 1),        
        'ܝܘܡܐܐܚܪܢܐ': today + timedelta(days= 2),
    }
    timesDict = {
        'ܩܕܡܛܗܪܐ': timedelta(hours=8),
        'ܩܕܡܬܐ': timedelta(hours=8),
        'ܒܬܪܛܗܪܐ': timedelta(hours=15),
        'ܒܬܪܟܘܬܪܐ': timedelta(hours=15),
    }
    
    exactDict = {
        'ܗܫܐ': anchorDate,
    }
    nextWords = ["ܒܬܪ", "ܡܢ ܒܬܪ", "ܒܬܪ ܗܕܐ", "ܒܬܪܝܐ"]
    prevWords = ["ܩܕܝܡܐܝܬ", "ܡܩܕܡ ܕ", "ܩܕܡ", "ܡܢ ܩܕܡ", "ܩܘܕܡܐܝܬ", "ܩܕܡ ܐܕܝܐ"]
    words = _parse_sentence(text)
    mode = 'none'
    number_seen = None
    delta_seen = timedelta(0)
    remainder = []
    result = None
    for word in words:
        print(f'HANDLED - BEGIN, mode {mode}')    
        print(f'extract_datetime // word at top {word}')
        handled = 1
        
        if mode == 'finished':
            print(f'extract_datetime // mode is finished: remainder {word}')
            #remainder.append(word)
        
        #if word[1:] == 'ܘ' and mode[:5] == 'delta':
        #    print(f'extract_datetime // ܘ and mode = {mode[:5]}')
        #    word = word[1:]
        
        if type(word) == tuple:
            print(f'extract_datetime // tuple {type(word)}, word is == {word}')
            number_seen = word
        elif word in weekday_names:
            dayOffset = (weekday_names.index(word) + 1) - today_weekday
            if dayOffset < 0:
                dayOffset += 7
            result = today + timedelta(days=dayOffset)
            mode = 'time'
        elif word in exactDict:
            result = exactDict[word]
            print(f'extract_datetime // exactDict {result}')
            mode = 'finished'
        elif word in daysDict:
            result = daysDict[word]
            print(f'extract_datetime // daysDict {result}')
            mode = 'time'
        elif word in timesDict and mode == 'time':
            result += timesDict[word]
            print(f'extract_datetime // timesDict {result}')    
            mode = 'finished'
        elif word in _date_units:
            print(f'extract_datetime // date_units {word}')
            k = 1
            print(f'NUMBER_SEEN: _date_units: {number_seen[0]}, mode {mode}')
            if number_seen:
                k = number_seen[0]
                number_seen = None
            delta_seen += _date_units[word] * k
            if mode != 'delta_time':
                mode = 'delta_date'
        elif word in _time_units:
            print(f'extract_datetime // time_units {word}')
            k = 1
            print(f'NUMBER SEEN: _time_units: {number_seen[0]}, mode {mode}')
            if number_seen:
                print(f'extract_datetime // number_seen = yes')
                k = number_seen[0]
                print(f'extract_datetime // number_seen {k}')
                number_seen = None
            delta_seen += _time_units[word] * k
            #print(f'extract_datetime // number_seen[0] {number_seen[0]}, _time_units {_time_units[word]}')
            mode = 'delta_time'
            print(f'extract_datetime // delta_seen {delta_seen}, mode {mode}')
        elif word in nextWords or word in prevWords:
            # Give up instead of incorrect result
            if mode == 'time':
                return None
            sign = 1 if word in nextWords else -1
            if mode == 'delta_date':
                result = today + delta_seen
                mode = 'time'
            elif mode == 'delta_time':
                result = anchorDate + delta_seen
                mode = 'finished'
            else:
                handled = 0
        else:
            handled = 0


        if mode == 'delta_date':
            result = today + delta_seen
            print(f'extract_datetime // delta_DATE // the result is {result} ')
            mode = 'delta_time'
        elif mode == 'delta_time':
            result = anchorDate + delta_seen
            print(f'extract_datetime // delta_TIME // the result is {result} ')
            mode = 'finished'
#        else:
#            result = anchorDate

        if handled == 1:
            print(f'extract_datetime // it is handled, mode {mode}')
            print(f'HANDLED - END, mode {mode}')    
            continue   
        if number_seen:
            print(f'extract_datetime // if number_seen (at end): {number_seen[1]} ')
            remainder.extend(number_seen[1])
            number_seen = None   
        if result == None:
            result = anchorDate 
#        else:
#            print(f'extract_datetime // it is not handled ')
#            handled = 0
#            result = anchorDate

        # BUG? duplicates remainders
        #print(f'extract_datetime // what is this remainder.append(word)? // {word}')
        remainder.append(word)

    print(f'extract_datetime // result {result}, remainder {remainder}')    
    return (result, " ".join(remainder))

def is_fractional_syr(text):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        text (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """

    def partition_text (text):
        """
        This function takes text, partitions and cleans it

        Args:
            text (str): the string to partition
        Returns:
            (dict) or (bool): False if it does not have the separator, ܡܢ, 
            otherwise return the dict
                        
        """
        dict_partition = []

        # [0] is word before the separator
        # [1] is the separator, ܡܢ
        # [2] is the word after the separator
        parted_text = text.partition(_SYRIAC_SEPARATOR)

        # This is not a fraction
        if parted_text[1] != _SYRIAC_SEPARATOR:
            return False

        for part in parted_text:
            # Remove whitespace
            part.replace(' ', '') 

        dict_partition = {
            'numerator' : parted_text[0], 
            'denominator' : parted_text[2]
        }

        return dict_partition


    print(f'FRACTIONS // in here with word {text}')
    # Exception for half or ܦܠܓܐ
    if text in _SYRIAC_FRACTIONS_HALF:
        fraction = 0.5
        return fraction

    # Check to see if the word is in the list
    if text in list(_SYRIAC_FRACTIONS.values()):
        # Find the key and use that as the denominator
        denominator = [key for key, value in _SYRIAC_FRACTIONS.items() if value == text]
        # Turn the returned list to an int
        denominator = int(' '.join([str(elem) for elem in denominator]))

        fraction = 1/denominator

        return fraction
    # Otherwise, it will be in the form of [denominator ܡܢ numerator] or ܬܠܬܐ ܡܢ ܥܣܪܐ
    else:
        print(f'FRACTIONS // at else {text}')
        
        if partition_text(text):
            # Just retrieve the dictionary containing the numerator and denominator
            dict_partition = partition_text(text)
            for fract_part, text in dict_partition.items():

                if text in _SYRIAC_ONES or text in _SYRIAC_ONES_FEM:
                    if text in _SYRIAC_ONES:
                        temp = _SYRIAC_ONES.index(text)
                    elif text in _SYRIAC_ONES_FEM:
                        temp = _SYRIAC_ONES_FEM.index(text)
                elif text in _SYRIAC_TENS:
                    temp = _SYRIAC_TENS.index(text)*10
                elif text in _SYRIAC_HUNDREDS:
                    temp = _SYRIAC_HUNDREDS.index(text)*100
                elif text in _SYRIAC_LARGE:
                    if _SYRIAC_LARGE.index(text) == 1:
                        temp = 1
                    temp *= 10**(3*_SYRIAC_LARGE.index(text))                   
                else:
                    return False 

                if fract_part == 'numerator':
                    numerator = temp
                else:
                    denominator = temp

            print(f'BOTTOM: numerator {numerator}')
            print(f'BOTTOM: denominator {denominator}')
            fraction = numerator/denominator
            return fraction
            #return False
        else:
            return False
        
    print(f'FRACTIONS // got nothing')    
    return False     

def get_gender_syr(word, context=""):
    """ Guess the gender of a word

    Some languages assign genders to specific words.  This method will attempt
    to determine the gender, optionally using the provided context sentence.

    Args:
        word (str): The word to look up
        context (str, optional): String containing word, for context

    Returns:
        str: The code "m" (male), "f" (female) or "n" (neutral) for the gender,
             or None if unknown/or unused in the given language.
    """
    word = word.rstrip("s")
    gender = False
    words = context.split(" ")
    for idx, w in enumerate(words):
        if w == word and idx != 0:
            previous = words[idx - 1]
            gender = get_gender_syr(previous)
            break
    if not gender:
        if word[-1] == "a":
            gender = "f"
        if word[-1] == "o" or word[-1] == "e":
            gender = "m"
    return gender

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

    words = _parse_sentence(text)    
    result = []
    for word in words:
        print(f'extract_numbers_syr // word {word}')
        if type(word) == tuple:
            result.append(word[0])
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
    word = extract_numbers_syr(text, ordinals=ordinals)
    if (len(word) == 0):
        return False
    return word[0]
