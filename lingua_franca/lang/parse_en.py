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
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, date, time

from lingua_franca.lang.parse_common import DurationResolution, invert_dict, ReplaceableNumber, \
    partition_list, tokenize, Token, Normalizer, Season, Hemisphere, DateResolution, TimeResolution
from lingua_franca.lang.common_data_en import _ARTICLES_EN, _NUM_STRING_EN, \
    _LONG_ORDINAL_EN, _LONG_SCALE_EN, _SHORT_SCALE_EN, _SHORT_ORDINAL_EN, \
    _SEASONS_EN, _HEMISPHERES_EN, _ORDINAL_BASE_EN

import re
import json
import math
from lingua_franca import resolve_resource_file
from lingua_franca.time import now_local, DAYS_IN_1_MONTH, DAYS_IN_1_YEAR
from lingua_franca.time import date_to_season, season_to_date, \
    get_season_range, next_season_date, last_season_date, get_ordinal, \
    get_weekend_range, get_week_range, get_century_range, \
    get_millennium_range, get_year_range, get_month_range, get_decade_range, \
    int_to_weekday, int_to_month, weekday_to_int, month_to_int, now_local


try:
    from simple_NER.annotators.locations import LocationNER
    _ner = LocationNER()
except ImportError:
    _ner = None
    print("Location extraction disabled")
    print("Run pip install simple_NER>=0.4.1")


def generate_plurals_en(originals):
    """
    Return a new set or dict containing the plural form of the original values,

    In English this means all with 's' appended to them.

    Args:
        originals set(str) or dict(str, any): values to pluralize

    Returns:
        set(str) or dict(str, any)

    """
    if isinstance(originals, dict):
        return {key + 's': value for key, value in originals.items()}
    return {value + "s" for value in originals}


# negate next number (-2 = 0 - 2)
_NEGATIVES = {"negative", "minus"}

# sum the next number (twenty two = 20 + 2)
_SUMS = {'twenty', '20', 'thirty', '30', 'forty', '40', 'fifty', '50',
         'sixty', '60', 'seventy', '70', 'eighty', '80', 'ninety', '90'}

_MULTIPLIES_LONG_SCALE_EN = set(_LONG_SCALE_EN.values()) | \
                            generate_plurals_en(_LONG_SCALE_EN.values())

_MULTIPLIES_SHORT_SCALE_EN = set(_SHORT_SCALE_EN.values()) | \
                             generate_plurals_en(_SHORT_SCALE_EN.values())

# split sentence parse separately and sum ( 2 and a half = 2 + 0.5 )
_FRACTION_MARKER = {"and"}

# decimal marker ( 1 point 5 = 1 + 0.5)
_DECIMAL_MARKER = {"point", "dot"}

_STRING_NUM_EN = invert_dict(_NUM_STRING_EN)
_STRING_NUM_EN.update(generate_plurals_en(_STRING_NUM_EN))
_STRING_NUM_EN.update({
    "half": 0.5,
    "halves": 0.5,
    "couple": 2
})

_STRING_SHORT_ORDINAL_EN = invert_dict(_SHORT_ORDINAL_EN)
_STRING_LONG_ORDINAL_EN = invert_dict(_LONG_ORDINAL_EN)


def _convert_words_to_numbers_en(text, short_scale=True, ordinals=False):
    """
    Convert words in a string into their equivalent numbers.
    Args:
        text str:
        short_scale boolean: True if short scale numbers should be used.
        ordinals boolean: True if ordinals (e.g. first, second, third) should
                          be parsed to their number values (1, 2, 3...)

    Returns:
        str
        The original text, with numbers subbed in where appropriate.

    """
    text = text.lower()
    tokens = tokenize(text)
    numbers_to_replace = \
        _extract_numbers_with_text_en(tokens, short_scale, ordinals)
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


def _extract_numbers_with_text_en(tokens, short_scale=True,
                                  ordinals=False, fractional_numbers=True):
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
            _extract_number_with_text_en(tokens, short_scale,
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


def _extract_number_with_text_en(tokens, short_scale=True,
                                 ordinals=False, fractional_numbers=True):
    """
    This function extracts a number from a list of Tokens.

    Args:
        tokens str: the string to normalize
        short_scale (bool): use short scale if True, long scale if False
        ordinals (bool): consider ordinal numbers, third=3 instead of 1/3
        fractional_numbers (bool): True if we should look for fractions and
                                   decimals.
    Returns:
        ReplaceableNumber

    """
    number, tokens = \
        _extract_number_with_text_en_helper(tokens, short_scale,
                                            ordinals, fractional_numbers)
    while tokens and tokens[0].word in _ARTICLES_EN:
        tokens.pop(0)
    return ReplaceableNumber(number, tokens)


def _extract_number_with_text_en_helper(tokens,
                                        short_scale=True, ordinals=False,
                                        fractional_numbers=True):
    """
    Helper for _extract_number_with_text_en.

    This contains the real logic for parsing, but produces
    a result that needs a little cleaning (specific, it may
    contain leading articles that can be trimmed off).

    Args:
        tokens [Token]:
        short_scale boolean:
        ordinals boolean:
        fractional_numbers boolean:

    Returns:
        int or float, [Tokens]

    """
    if fractional_numbers:
        fraction, fraction_text = \
            _extract_fraction_with_text_en(tokens, short_scale, ordinals)
        if fraction:
            return fraction, fraction_text

        decimal, decimal_text = \
            _extract_decimal_with_text_en(tokens, short_scale, ordinals)
        if decimal:
            return decimal, decimal_text

    return _extract_whole_number_with_text_en(tokens, short_scale, ordinals)


def _extract_fraction_with_text_en(tokens, short_scale, ordinals):
    """
    Extract fraction numbers from a string.

    This function handles text such as '2 and 3/4'. Note that "one half" or
    similar will be parsed by the whole number function.

    Args:
        tokens [Token]: words and their indexes in the original string.
        short_scale boolean:
        ordinals boolean:

    Returns:
        (int or float, [Token])
        The value found, and the list of relevant tokens.
        (None, None) if no fraction value is found.

    """
    for c in _FRACTION_MARKER:
        partitions = partition_list(tokens, lambda t: t.word == c)

        if len(partitions) == 3:
            numbers1 = \
                _extract_numbers_with_text_en(partitions[0], short_scale,
                                              ordinals,
                                              fractional_numbers=False)
            numbers2 = \
                _extract_numbers_with_text_en(partitions[2], short_scale,
                                              ordinals,
                                              fractional_numbers=True)

            if not numbers1 or not numbers2:
                return None, None

            # ensure first is not a fraction and second is a fraction
            num1 = numbers1[-1]
            num2 = numbers2[0]
            if num1.value >= 1 and 0 < num2.value < 1:
                return num1.value + num2.value, \
                       num1.tokens + partitions[1] + num2.tokens

    return None, None


def _extract_decimal_with_text_en(tokens, short_scale, ordinals):
    """
    Extract decimal numbers from a string.

    This function handles text such as '2 point 5'.

    Notes:
        While this is a helper for extractnumber_en, it also depends on
        extractnumber_en, to parse out the components of the decimal.

        This does not currently handle things like:
            number dot number number number

    Args:
        tokens [Token]: The text to parse.
        short_scale boolean:
        ordinals boolean:

    Returns:
        (float, [Token])
        The value found and relevant tokens.
        (None, None) if no decimal value is found.

    """
    for c in _DECIMAL_MARKER:
        partitions = partition_list(tokens, lambda t: t.word == c)

        if len(partitions) == 3:
            numbers1 = \
                _extract_numbers_with_text_en(partitions[0], short_scale,
                                              ordinals,
                                              fractional_numbers=False)
            numbers2 = \
                _extract_numbers_with_text_en(partitions[2], short_scale,
                                              ordinals,
                                              fractional_numbers=False)

            if not numbers1 or not numbers2:
                return None, None

            number = numbers1[-1]
            decimal = numbers2[0]

            # TODO handle number dot number number number
            if "." not in str(decimal.text):
                return number.value + float('0.' + str(decimal.value)), \
                       number.tokens + partitions[1] + decimal.tokens
    return None, None


def _extract_whole_number_with_text_en(tokens, short_scale, ordinals):
    """
    Handle numbers not handled by the decimal or fraction functions. This is
    generally whole numbers. Note that phrases such as "one half" will be
    handled by this function, while "one and a half" are handled by the
    fraction function.

    Args:
        tokens [Token]:
        short_scale boolean:
        ordinals boolean:

    Returns:
        int or float, [Tokens]
        The value parsed, and tokens that it corresponds to.

    """
    multiplies, string_num_ordinal, string_num_scale = \
        _initialize_number_data(short_scale)

    number_words = []  # type: [Token]
    val = False
    prev_val = None
    next_val = None
    to_sum = []
    for idx, token in enumerate(tokens):
        current_val = None
        if next_val:
            next_val = None
            continue

        word = token.word
        if word in _ARTICLES_EN or word in _NEGATIVES:
            number_words.append(token)
            continue

        prev_word = tokens[idx - 1].word if idx > 0 else ""
        next_word = tokens[idx + 1].word if idx + 1 < len(tokens) else ""

        if is_numeric(word[:-2]) and \
                (word.endswith("st") or word.endswith("nd") or
                 word.endswith("rd") or word.endswith("th")):

            # explicit ordinals, 1st, 2nd, 3rd, 4th.... Nth
            word = word[:-2]

            # handle nth one
            if next_word == "one":
                # would return 1 instead otherwise
                tokens[idx + 1] = Token("", idx)
                next_word = ""

        if word not in string_num_scale and \
                word not in _STRING_NUM_EN and \
                word not in _SUMS and \
                word not in multiplies and \
                not (ordinals and word in string_num_ordinal) and \
                not is_numeric(word) and \
                not isFractional_en(word, short_scale=short_scale) and \
                not look_for_fractions(word.split('/')):
            words_only = [token.word for token in number_words]
            if number_words and not all([w in _ARTICLES_EN |
                                         _NEGATIVES for w in words_only]):
                break
            else:
                number_words = []
                continue
        elif word not in multiplies \
                and prev_word not in multiplies \
                and prev_word not in _SUMS \
                and not (ordinals and prev_word in string_num_ordinal) \
                and prev_word not in _NEGATIVES \
                and prev_word not in _ARTICLES_EN:
            number_words = [token]
        elif prev_word in _SUMS and word in _SUMS:
            number_words = [token]
        else:
            number_words.append(token)

        # is this word already a number ?
        if is_numeric(word):
            if word.isdigit():  # doesn't work with decimals
                val = int(word)
            else:
                val = float(word)
            current_val = val

        # is this word the name of a number ?
        if word in _STRING_NUM_EN:
            val = _STRING_NUM_EN.get(word)
            current_val = val
        elif word in string_num_scale:
            val = string_num_scale.get(word)
            current_val = val
        elif ordinals and word in string_num_ordinal:
            val = string_num_ordinal[word]
            current_val = val

        # is the prev word an ordinal number and current word is one?
        # second one, third one
        if ordinals and prev_word in string_num_ordinal and val is 1:
            val = prev_val

        # is the prev word a number and should we sum it?
        # twenty two, fifty six
        if (prev_word in _SUMS and val and val < 10) or all([prev_word in
                                                             multiplies,
                                                             val < prev_val if prev_val else False]):
            val = prev_val + val

        # is the prev word a number and should we multiply it?
        # twenty hundred, six hundred
        if word in multiplies:
            if not prev_val:
                prev_val = 1
            val = prev_val * val

        # is this a spoken fraction?
        # half cup
        if val is False:
            val = isFractional_en(word, short_scale=short_scale)
            current_val = val

        # 2 fifths
        if not ordinals:
            next_val = isFractional_en(next_word, short_scale=short_scale)
            if next_val:
                if not val:
                    val = 1
                val = val * next_val
                number_words.append(tokens[idx + 1])

        # is this a negative number?
        if val and prev_word and prev_word in _NEGATIVES:
            val = 0 - val

        # let's make sure it isn't a fraction
        if not val:
            # look for fractions like "2/3"
            aPieces = word.split('/')
            if look_for_fractions(aPieces):
                val = float(aPieces[0]) / float(aPieces[1])
                current_val = val

        else:
            if all([
                prev_word in _SUMS,
                word not in _SUMS,
                word not in multiplies,
                current_val >= 10]):
                # Backtrack - we've got numbers we can't sum.
                number_words.pop()
                val = prev_val
                break
            prev_val = val

            if word in multiplies and next_word not in multiplies:
                # handle long numbers
                # six hundred sixty six
                # two million five hundred thousand
                #
                # This logic is somewhat complex, and warrants
                # extensive documentation for the next coder's sake.
                #
                # The current word is a power of ten. `current_val` is
                # its integer value. `val` is our working sum
                # (above, when `current_val` is 1 million, `val` is
                # 2 million.)
                #
                # We have a dict `string_num_scale` containing [value, word]
                # pairs for "all" powers of ten: string_num_scale[10] == "ten.
                #
                # We need go over the rest of the tokens, looking for other
                # powers of ten. If we find one, we compare it with the current
                # value, to see if it's smaller than the current power of ten.
                #
                # Numbers which are not powers of ten will be passed over.
                #
                # If all the remaining powers of ten are smaller than our
                # current value, we can set the current value aside for later,
                # and begin extracting another portion of our final result.
                # For example, suppose we have the following string.
                # The current word is "million".`val` is 9000000.
                # `current_val` is 1000000.
                #
                #    "nine **million** nine *hundred* seven **thousand**
                #     six *hundred* fifty seven"
                #
                # Iterating over the rest of the string, the current
                # value is larger than all remaining powers of ten.
                #
                # The if statement passes, and nine million (9000000)
                # is appended to `to_sum`.
                #
                # The main variables are reset, and the main loop begins
                # assembling another number, which will also be appended
                # under the same conditions.
                #
                # By the end of the main loop, to_sum will be a list of each
                # "place" from 100 up: [9000000, 907000, 600]
                #
                # The final three digits will be added to the sum of that list
                # at the end of the main loop, to produce the extracted number:
                #
                #    sum([9000000, 907000, 600]) + 57
                # == 9,000,000 + 907,000 + 600 + 57
                # == 9,907,657
                #
                # >>> foo = "nine million nine hundred seven thousand six
                #            hundred fifty seven"
                # >>> extract_number(foo)
                # 9907657

                time_to_sum = True
                for other_token in tokens[idx + 1:]:
                    if other_token.word in multiplies:
                        if string_num_scale[other_token.word] >= current_val:
                            time_to_sum = False
                        else:
                            continue
                    if not time_to_sum:
                        break
                if time_to_sum:
                    to_sum.append(val)
                    val = 0
                    prev_val = 0

    if val is not None and to_sum:
        val += sum(to_sum)

    return val, number_words


def _initialize_number_data(short_scale):
    """
    Generate dictionaries of words to numbers, based on scale.

    This is a helper function for _extract_whole_number.

    Args:
        short_scale boolean:

    Returns:
        (set(str), dict(str, number), dict(str, number))
        multiplies, string_num_ordinal, string_num_scale

    """
    multiplies = _MULTIPLIES_SHORT_SCALE_EN if short_scale \
        else _MULTIPLIES_LONG_SCALE_EN

    string_num_ordinal_en = _STRING_SHORT_ORDINAL_EN if short_scale \
        else _STRING_LONG_ORDINAL_EN

    string_num_scale_en = _SHORT_SCALE_EN if short_scale else _LONG_SCALE_EN
    string_num_scale_en = invert_dict(string_num_scale_en)
    string_num_scale_en.update(generate_plurals_en(string_num_scale_en))
    return multiplies, string_num_ordinal_en, string_num_scale_en


def extractnumber_en(text, short_scale=True, ordinals=False):
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
    return _extract_number_with_text_en(tokenize(text.lower()),
                                        short_scale, ordinals).value


def extract_duration_en(text, resolution=DurationResolution.TIMEDELTA,
                        replace_token=""):
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
        resolution (DurationResolution): format to return extracted duration on
        replace_token (str): string to replace consumed words with

    Returns:
        (timedelta, str):
                    A tuple containing the duration and the remaining text
                    not consumed in the parsing. The first value will
                    be None if no duration is found. The text returned
                    will have whitespace stripped from the ends.
    """
    if not text:
        return None

    pattern = r"(?P<value>\d+(?:\.?\d+)?)(?:\s+|\-){unit}s?"
    # text normalization
    original_text = text
    text = _convert_words_to_numbers_en(text)
    text = text.replace("centuries", "century").replace("millenia",
                                                        "millennium")
    text = text.replace("a day", "1 day").replace("a year", "1 year") \
        .replace("a decade", "1 decade").replace("a century", "1 century") \
        .replace("a millennium", "1 millennium")

    # we are always replacing 2 words, {N} {unit}
    if replace_token:
        replace_token += " " + replace_token

    if resolution == DurationResolution.TIMEDELTA:
        si_units = {
            'microseconds': None,
            'milliseconds': None,
            'seconds': None,
            'minutes': None,
            'hours': None,
            'days': None,
            'weeks': None
        }

        units = ['months', 'years', 'decades', 'centurys', 'millenniums'] + \
                list(si_units.keys())

        for unit in units:
            unit_pattern = pattern.format(
                unit=unit[:-1])  # remove 's' from unit
            matches = re.findall(unit_pattern, text)
            value = sum(map(float, matches))
            text = re.sub(unit_pattern, replace_token, text)
            if unit == "days":
                if si_units["days"] is None:
                    si_units["days"] = 0
                si_units["days"] += value
            elif unit == "months":
                if si_units["days"] is None:
                    si_units["days"] = 0
                si_units["days"] += DAYS_IN_1_MONTH * value
            elif unit == "years":
                if si_units["days"] is None:
                    si_units["days"] = 0
                si_units["days"] += DAYS_IN_1_YEAR * value
            elif unit == "decades":
                if si_units["days"] is None:
                    si_units["days"] = 0
                si_units["days"] += 10 * DAYS_IN_1_YEAR * value
            elif unit == "centurys":
                if si_units["days"] is None:
                    si_units["days"] = 0
                si_units["days"] += 100 * DAYS_IN_1_YEAR * value
            elif unit == "millenniums":
                if si_units["days"] is None:
                    si_units["days"] = 0
                si_units["days"] += 1000 * DAYS_IN_1_YEAR * value
            else:
                si_units[unit] = value
        duration = timedelta(**si_units) if any(si_units.values()) else None
    elif resolution in [DurationResolution.RELATIVEDELTA,
                        DurationResolution.RELATIVEDELTA_APPROXIMATE,
                        DurationResolution.RELATIVEDELTA_FALLBACK,
                        DurationResolution.RELATIVEDELTA_STRICT]:
        relative_units = {
            'microseconds': None,
            'seconds': None,
            'minutes': None,
            'hours': None,
            'days': None,
            'weeks': None,
            'months': None,
            'years': None
        }

        units = ['decades', 'centurys', 'millenniums', 'milliseconds'] + \
                list(relative_units.keys())
        for unit in units:
            unit_pattern = pattern.format(
                unit=unit[:-1])  # remove 's' from unit
            matches = re.findall(unit_pattern, text)
            value = sum(map(float, matches))
            text = re.sub(unit_pattern, replace_token, text)
            # relativedelta does not support milliseconds
            if unit == "milliseconds":
                if relative_units["microseconds"] is None:
                    relative_units["microseconds"] = 0
                relative_units["microseconds"] += value * 1000
            elif unit == "microseconds":
                if relative_units["microseconds"] is None:
                    relative_units["microseconds"] = 0
                relative_units["microseconds"] += value
            # relativedelta does not support decades, centuries or millennia
            elif unit == "years":
                if relative_units["years"] is None:
                    relative_units["years"] = 0
                relative_units["years"] += value
            elif unit == "decades":
                if relative_units["years"] is None:
                    relative_units["years"] = 0
                relative_units["years"] += value * 10
            elif unit == "centurys":
                if relative_units["years"] is None:
                    relative_units["years"] = 0
                relative_units["years"] += value * 100
            elif unit == "millenniums":
                if relative_units["years"] is None:
                    relative_units["years"] = 0
                relative_units["years"] += value * 1000
            else:
                relative_units[unit] = value

        # microsecond, month, year must be ints
        relative_units["microseconds"] = int(relative_units["microseconds"])
        if resolution == DurationResolution.RELATIVEDELTA_FALLBACK:
            for unit in ["months", "years"]:
                value = relative_units[unit]
                _leftover, _ = math.modf(value)
                if _leftover != 0:
                    print("[WARNING] relativedelta requires {unit} to be an "
                          "integer".format(unit=unit))
                    # fallback to timedelta resolution
                    return extract_duration_en(original_text,
                                               DurationResolution.TIMEDELTA,
                                               replace_token)
                relative_units[unit] = int(value)
        elif resolution == DurationResolution.RELATIVEDELTA_APPROXIMATE:
            _leftover, year = math.modf(relative_units["years"])
            relative_units["months"] += 12 * _leftover
            relative_units["years"] = int(year)
            _leftover, month = math.modf(relative_units["months"])
            relative_units["days"] += DAYS_IN_1_MONTH * _leftover
            relative_units["months"] = int(month)
        else:
            for unit in ["months", "years"]:
                value = relative_units[unit]
                _leftover, _ = math.modf(value)
                if _leftover != 0:
                    raise ValueError("relativedelta requires {unit} to be an "
                                     "integer".format(unit=unit))
                relative_units[unit] = int(value)
        duration = relativedelta(**relative_units) if \
            any(relative_units.values()) else None
    else:
        microseconds = 0
        units = ['months', 'years', 'decades', 'centurys', 'millenniums',
                 "microseconds", "milliseconds", "seconds", "minutes",
                 "hours", "days", "weeks"]

        for unit in units:
            unit_pattern = pattern.format(
                unit=unit[:-1])  # remove 's' from unit
            matches = re.findall(unit_pattern, text)
            value = sum(map(float, matches))
            text = re.sub(unit_pattern, replace_token, text)
            if unit == "microseconds":
                microseconds += value
            elif unit == "milliseconds":
                microseconds += value * 1000
            elif unit == "seconds":
                microseconds += value * 1000 * 1000
            elif unit == "minutes":
                microseconds += value * 1000 * 1000 * 60
            elif unit == "hours":
                microseconds += value * 1000 * 1000 * 60 * 60
            elif unit == "days":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24
            elif unit == "weeks":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24 * 7
            elif unit == "months":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24 * \
                                DAYS_IN_1_MONTH
            elif unit == "years":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24 * \
                                DAYS_IN_1_YEAR
            elif unit == "decades":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24 * \
                                DAYS_IN_1_YEAR * 10
            elif unit == "centurys":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24 * \
                                DAYS_IN_1_YEAR * 100
            elif unit == "millenniums":
                microseconds += value * 1000 * 1000 * 60 * 60 * 24 * \
                                DAYS_IN_1_YEAR * 1000

        if resolution == DurationResolution.TOTAL_MICROSECONDS:
            duration = microseconds
        elif resolution == DurationResolution.TOTAL_MILLISECONDS:
            duration = microseconds / 1000
        elif resolution == DurationResolution.TOTAL_SECONDS:
            duration = microseconds / (1000 * 1000)
        elif resolution == DurationResolution.TOTAL_MINUTES:
            duration = microseconds / (1000 * 1000 * 60)
        elif resolution == DurationResolution.TOTAL_HOURS:
            duration = microseconds / (1000 * 1000 * 60 * 60)
        elif resolution == DurationResolution.TOTAL_DAYS:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24)
        elif resolution == DurationResolution.TOTAL_WEEKS:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24 * 7)
        elif resolution == DurationResolution.TOTAL_MONTHS:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24 *
                                       DAYS_IN_1_MONTH)
        elif resolution == DurationResolution.TOTAL_YEARS:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24 *
                                       DAYS_IN_1_YEAR)
        elif resolution == DurationResolution.TOTAL_DECADES:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24 *
                                       DAYS_IN_1_YEAR * 10)
        elif resolution == DurationResolution.TOTAL_CENTURIES:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24 *
                                       DAYS_IN_1_YEAR * 100)
        elif resolution == DurationResolution.TOTAL_MILLENNIUMS:
            duration = microseconds / (1000 * 1000 * 60 * 60 * 24 *
                                       DAYS_IN_1_YEAR * 1000)
        else:
            raise ValueError
    if not replace_token:
        text = text.strip()
    return duration, text


def extract_datetime_en(string, dateNow, default_time):
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
        string (str): string containing date words
        dateNow (datetime): A reference date/time for "tommorrow", etc
        default_time (time): Time to set if no time was found in the string

    Returns:
        [datetime, str]: An array containing the datetime and the remaining
                         text not consumed in the parsing, or None if no
                         date or time related text was found.
    """

    def clean_string(s):
        # clean unneeded punctuation and capitalization among other things.
        s = s.lower().replace('?', '').replace('.', '').replace(',', '') \
            .replace(' the ', ' ').replace(' a ', ' ').replace(' an ', ' ') \
            .replace("o' clock", "o'clock").replace("o clock", "o'clock") \
            .replace("o ' clock", "o'clock").replace("o 'clock", "o'clock") \
            .replace("oclock", "o'clock").replace("couple", "2") \
            .replace("centuries", "century").replace("decades", "decade") \
            .replace("millenniums", "millennium")

        wordList = s.split()
        for idx, word in enumerate(wordList):
            word = word.replace("'s", "")

            ordinals = ["rd", "st", "nd", "th"]
            if word[0].isdigit():
                for ordinal in ordinals:
                    # "second" is the only case we should not do this
                    if ordinal in word and "second" not in word:
                        word = word.replace(ordinal, "")
            wordList[idx] = word

        return wordList

    def date_found():
        return found or \
               (
                       datestr != "" or
                       yearOffset != 0 or monthOffset != 0 or
                       dayOffset is True or hrOffset != 0 or
                       hrAbs or minOffset != 0 or
                       minAbs or secOffset != 0
               )

    if string == "" or not dateNow:
        return None

    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    today = dateNow.strftime("%w")
    currentYear = dateNow.strftime("%Y")
    fromFlag = False
    datestr = ""
    hasYear = False
    timeQualifier = ""

    timeQualifiersAM = ['morning']
    timeQualifiersPM = ['afternoon', 'evening', 'night', 'tonight']
    timeQualifiersList = set(timeQualifiersAM + timeQualifiersPM)
    markers = ['at', 'in', 'on', 'by', 'this', 'around', 'for', 'of', "within"]
    days = ['monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday']
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november',
              'december']
    recur_markers = days + [d + 's' for d in days] + ['weekend', 'weekday',
                                                      'weekends', 'weekdays']
    monthsShort = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july', 'aug',
                   'sept', 'oct', 'nov', 'dec']
    year_multiples = ["decade", "century", "millennium"]
    day_multiples = ["weeks", "months", "years"]

    words = clean_string(string)

    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""

        # this isn't in clean string because I don't want to save back to words
        word = word.rstrip('s')
        start = idx
        used = 0
        # save timequalifier for later
        if word == "ago" and dayOffset:
            dayOffset = - dayOffset
            used += 1
        if word == "now" and not datestr:
            resultStr = " ".join(words[idx + 1:])
            resultStr = ' '.join(resultStr.split())
            extractedDate = dateNow.replace(microsecond=0)
            return [extractedDate, resultStr]
        elif wordNext in year_multiples:
            multiplier = None
            if is_numeric(word):
                multiplier = extractnumber_en(word)
            multiplier = multiplier or 1
            multiplier = int(multiplier)
            used += 2
            if wordNext == "decade":
                yearOffset = multiplier * 10
            elif wordNext == "century":
                yearOffset = multiplier * 100
            elif wordNext == "millennium":
                yearOffset = multiplier * 1000
        # couple of
        elif word == "2" and wordNext == "of" and \
                wordNextNext in year_multiples:
            multiplier = 2
            used += 3
            if wordNextNext == "decade":
                yearOffset = multiplier * 10
            elif wordNextNext == "century":
                yearOffset = multiplier * 100
            elif wordNextNext == "millennium":
                yearOffset = multiplier * 1000
        elif word == "2" and wordNext == "of" and \
                wordNextNext in day_multiples:
            multiplier = 2
            used += 3
            if wordNextNext == "years":
                yearOffset = multiplier
            elif wordNextNext == "months":
                monthOffset = multiplier
            elif wordNextNext == "weeks":
                dayOffset = multiplier * 7
        elif word in timeQualifiersList:
            timeQualifier = word
        # parse today, tomorrow, day after tomorrow
        elif word == "today" and not fromFlag:
            dayOffset = 0
            used += 1
        elif word == "tomorrow" and not fromFlag:
            dayOffset = 1
            used += 1
        elif word == "day" and wordNext == "before" and wordNextNext == "yesterday" and not fromFlag:
            dayOffset = -2
            used += 3
        elif word == "before" and wordNext == "yesterday" and not fromFlag:
            dayOffset = -2
            used += 2
        elif word == "yesterday" and not fromFlag:
            dayOffset = -1
            used += 1
        elif (word == "day" and
              wordNext == "after" and
              wordNextNext == "tomorrow" and
              not fromFlag and
              (not wordPrev or not wordPrev[0].isdigit())):
            dayOffset = 2
            used = 3
            if wordPrev == "the":
                start -= 1
                used += 1
                # parse 5 days, 10 weeks, last week, next week
        elif word == "day":
            if wordPrev and wordPrev[0].isdigit():
                dayOffset += int(wordPrev)
                start -= 1
                used = 2
        elif word == "week" and not fromFlag and wordPrev:
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev) * 7
                start -= 1
                used = 2
            elif wordPrev == "next":
                dayOffset = 7
                start -= 1
                used = 2
            elif wordPrev == "last":
                dayOffset = -7
                start -= 1
                used = 2
                # parse 10 months, next month, last month
        elif word == "month" and not fromFlag and wordPrev:
            if wordPrev[0].isdigit():
                monthOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordPrev == "next":
                monthOffset = 1
                start -= 1
                used = 2
            elif wordPrev == "last":
                monthOffset = -1
                start -= 1
                used = 2
        # parse 5 years, next year, last year
        elif word == "year" and not fromFlag and wordPrev:
            if wordPrev[0].isdigit():
                yearOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordPrev == "next":
                yearOffset = 1
                start -= 1
                used = 2
            elif wordPrev == "last":
                yearOffset = -1
                start -= 1
                used = 2
        # parse Monday, Tuesday, etc., and next Monday,
        # last Tuesday, etc.
        elif word in days and not fromFlag:
            d = days.index(word)
            dayOffset = (d + 1) - int(today)
            used = 1
            if dayOffset < 0:
                dayOffset += 7
            if wordPrev == "next":
                if dayOffset <= 2:
                    dayOffset += 7
                used += 1
                start -= 1
            elif wordPrev == "last":
                dayOffset -= 7
                used += 1
                start -= 1
                # parse 15 of July, June 20th, Feb 18, 19 of February
        elif word in months or word in monthsShort and not fromFlag:
            try:
                m = months.index(word)
            except ValueError:
                m = monthsShort.index(word)
            used += 1
            datestr = months[m]
            if wordPrev and (wordPrev[0].isdigit() or
                             (wordPrev == "of" and wordPrevPrev[0].isdigit())):
                if wordPrev == "of" and wordPrevPrev[0].isdigit():
                    datestr += " " + words[idx - 2]
                    used += 1
                    start -= 1
                else:
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

            # if no date indicators found, it may not be the month of May
            # may "i/we" ...
            # "... may be"
            elif word == 'may' and wordNext in ['i', 'we', 'be']:
                datestr = ""

        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July
        validFollowups = days + months + monthsShort
        validFollowups.append("today")
        validFollowups.append("tomorrow")
        validFollowups.append("yesterday")
        validFollowups.append("next")
        validFollowups.append("last")
        validFollowups.append("now")
        validFollowups.append("this")
        if (word == "from" or word == "after") and wordNext in validFollowups:
            used = 2
            fromFlag = True
            if wordNext == "tomorrow":
                dayOffset += 1
            elif wordNext == "yesterday":
                dayOffset -= 1
            elif wordNext in days:
                d = days.index(wordNext)
                tmpOffset = (d + 1) - int(today)
                used = 2
                if tmpOffset < 0:
                    tmpOffset += 7
                dayOffset += tmpOffset
            elif wordNextNext and wordNextNext in days:
                d = days.index(wordNextNext)
                tmpOffset = (d + 1) - int(today)
                used = 3
                if wordNext == "next":
                    if dayOffset <= 2:
                        tmpOffset += 7
                    used += 1
                    start -= 1
                elif wordNext == "last":
                    tmpOffset -= 7
                    used += 1
                    start -= 1
                dayOffset += tmpOffset
        if used > 0:
            if start - 1 > 0 and words[start - 1] == "this":
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
        if word == "noon":
            hrAbs = 12
            used += 1
        elif word == "midnight":
            hrAbs = 0
            used += 1
        elif word == "morning":
            if hrAbs is None:
                hrAbs = 8
            used += 1
        elif word == "afternoon":
            if hrAbs is None:
                hrAbs = 15
            used += 1
        elif word == "evening":
            if hrAbs is None:
                hrAbs = 19
            used += 1
        elif word == "tonight" or word == "night":
            if hrAbs is None:
                hrAbs = 22
            # used += 1 ## NOTE this breaks other tests, TODO refactor me!

        # couple of time_unit
        elif word == "2" and wordNext == "of" and \
                wordNextNext in ["hours", "minutes", "seconds"]:
            used += 3
            if wordNextNext == "hours":
                hrOffset = 2
            elif wordNextNext == "minutes":
                minOffset = 2
            elif wordNextNext == "seconds":
                secOffset = 2
        # parse half an hour, quarter hour
        elif word == "hour" and \
                (wordPrev in markers or wordPrevPrev in markers):
            if wordPrev == "half":
                minOffset = 30
            elif wordPrev == "quarter":
                minOffset = 15
            elif wordPrevPrev == "quarter":
                minOffset = 15
                if idx > 2 and words[idx - 3] in markers:
                    words[idx - 3] = ""
                words[idx - 2] = ""
            elif wordPrev == "within":
                hrOffset = 1
            else:
                hrOffset = 1
            if wordPrevPrev in markers:
                words[idx - 2] = ""
                if wordPrevPrev == "this":
                    daySpecified = True
            words[idx - 1] = ""
            used += 1
            hrAbs = -1
            minAbs = -1
            # parse 5:00 am, 12:00 p.m., etc
        # parse in a minute
        elif word == "minute" and wordPrev == "in":
            minOffset = 1
            words[idx - 1] = ""
            used += 1
        # parse in a second
        elif word == "second" and wordPrev == "in":
            secOffset = 1
            words[idx - 1] = ""
            used += 1
        elif word[0].isdigit():
            isTime = True
            strHH = ""
            strMM = ""
            remainder = ""
            wordNextNextNext = words[idx + 3] \
                if idx + 3 < len(words) else ""
            if wordNext == "tonight" or wordNextNext == "tonight" or \
                    wordPrev == "tonight" or wordPrevPrev == "tonight" or \
                    wordNextNextNext == "tonight":
                remainder = "pm"
                used += 1
                if wordPrev == "tonight":
                    words[idx - 1] = ""
                if wordPrevPrev == "tonight":
                    words[idx - 2] = ""
                if wordNextNext == "tonight":
                    used += 1
                if wordNextNextNext == "tonight":
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
                    if nextWord == "am" or nextWord == "pm":
                        remainder = nextWord
                        used += 1

                    elif wordNext == "in" and wordNextNext == "the" and \
                            words[idx + 3] == "morning":
                        remainder = "am"
                        used += 3
                    elif wordNext == "in" and wordNextNext == "the" and \
                            words[idx + 3] == "afternoon":
                        remainder = "pm"
                        used += 3
                    elif wordNext == "in" and wordNextNext == "the" and \
                            words[idx + 3] == "evening":
                        remainder = "pm"
                        used += 3
                    elif wordNext == "in" and wordNextNext == "morning":
                        remainder = "am"
                        used += 2
                    elif wordNext == "in" and wordNextNext == "afternoon":
                        remainder = "pm"
                        used += 2
                    elif wordNext == "in" and wordNextNext == "evening":
                        remainder = "pm"
                        used += 2
                    elif wordNext == "this" and wordNextNext == "morning":
                        remainder = "am"
                        used = 2
                        daySpecified = True
                    elif wordNext == "this" and wordNextNext == "afternoon":
                        remainder = "pm"
                        used = 2
                        daySpecified = True
                    elif wordNext == "this" and wordNextNext == "evening":
                        remainder = "pm"
                        used = 2
                        daySpecified = True
                    elif wordNext == "at" and wordNextNext == "night":
                        if strHH and int(strHH) > 5:
                            remainder = "pm"
                        else:
                            remainder = "am"
                        used += 2

                    else:
                        if timeQualifier != "":
                            military = True
                            if strHH and int(strHH) <= 12 and \
                                    (timeQualifier in timeQualifiersPM):
                                strHH += str(int(strHH) + 12)

            else:
                # try to parse numbers without colons
                # 5 hours, 10 minutes etc.
                length = len(word)
                strNum = ""
                remainder = ""
                for i in range(length):
                    if word[i].isdigit():
                        strNum += word[i]
                    else:
                        remainder += word[i]

                if remainder == "":
                    remainder = wordNext.replace(".", "").lstrip().rstrip()
                if (
                        remainder == "pm" or
                        wordNext == "pm" or
                        remainder == "p.m." or
                        wordNext == "p.m."):
                    strHH = strNum
                    remainder = "pm"
                    used = 1
                elif (
                        remainder == "am" or
                        wordNext == "am" or
                        remainder == "a.m." or
                        wordNext == "a.m."):
                    strHH = strNum
                    remainder = "am"
                    used = 1
                elif (
                        remainder in recur_markers or
                        wordNext in recur_markers or
                        wordNextNext in recur_markers):
                    # Ex: "7 on mondays" or "3 this friday"
                    # Set strHH so that isTime == True
                    # when am or pm is not specified
                    strHH = strNum
                    used = 1
                else:
                    if (
                            int(strNum) > 100 and
                            (
                                    wordPrev == "o" or
                                    wordPrev == "oh"
                            )):
                        # 0800 hours (pronounced oh-eight-hundred)
                        strHH = str(int(strNum) // 100)
                        strMM = str(int(strNum) % 100)
                        military = True
                        if wordNext == "hours":
                            used += 1
                    elif (
                            (wordNext == "hours" or wordNext == "hour" or
                             remainder == "hours" or remainder == "hour") and
                            word[0] != '0' and
                            (
                                    int(strNum) < 100 or
                                    int(strNum) > 2400
                            )):
                        # ignores military time
                        # "in 3 hours"
                        hrOffset = int(strNum)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1

                    elif wordNext == "minutes" or wordNext == "minute" or \
                            remainder == "minutes" or remainder == "minute":
                        # "in 10 minutes"
                        minOffset = int(strNum)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext == "seconds" or wordNext == "second" \
                            or remainder == "seconds" or remainder == "second":
                        # in 5 seconds
                        secOffset = int(strNum)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif int(strNum) > 100:
                        # military time, eg. "3300 hours"
                        strHH = str(int(strNum) // 100)
                        strMM = str(int(strNum) % 100)
                        military = True
                        if wordNext == "hours" or wordNext == "hour" or \
                                remainder == "hours" or remainder == "hour":
                            used += 1
                    elif wordNext and wordNext[0].isdigit():
                        # military time, e.g. "04 38 hours"
                        strHH = strNum
                        strMM = wordNext
                        military = True
                        used += 1
                        if (wordNextNext == "hours" or
                                wordNextNext == "hour" or
                                remainder == "hours" or remainder == "hour"):
                            used += 1
                    elif (
                            wordNext == "" or wordNext == "o'clock" or
                            (
                                    wordNext == "in" and
                                    (
                                            wordNextNext == "the" or
                                            wordNextNext == timeQualifier
                                    )
                            ) or wordNext == 'tonight' or
                            wordNextNext == 'tonight'):

                        strHH = strNum
                        strMM = "00"
                        if wordNext == "o'clock":
                            used += 1

                        if wordNext == "in" or wordNextNext == "in":
                            used += (1 if wordNext == "in" else 2)
                            wordNextNextNext = words[idx + 3] \
                                if idx + 3 < len(words) else ""

                            if (wordNextNext and
                                    (wordNextNext in timeQualifier or
                                     wordNextNextNext in timeQualifier)):
                                if (wordNextNext in timeQualifiersPM or
                                        wordNextNextNext in timeQualifiersPM):
                                    remainder = "pm"
                                    used += 1
                                if (wordNextNext in timeQualifiersAM or
                                        wordNextNextNext in timeQualifiersAM):
                                    remainder = "am"
                                    used += 1

                        if timeQualifier != "":
                            if timeQualifier in timeQualifiersPM:
                                remainder = "pm"
                                used += 1

                            elif timeQualifier in timeQualifiersAM:
                                remainder = "am"
                                used += 1
                            else:
                                # TODO: Unsure if this is 100% accurate
                                used += 1
                                military = True
                    else:
                        isTime = False
            HH = int(strHH) if strHH else 0
            MM = int(strMM) if strMM else 0
            HH = HH + 12 if remainder == "pm" and HH < 12 else HH
            HH = HH - 12 if remainder == "am" and HH >= 12 else HH

            if (not military and
                    remainder not in ['am', 'pm', 'hours', 'minutes',
                                      "second", "seconds",
                                      "hour", "minute"] and
                    ((not daySpecified) or 0 <= dayOffset < 1)):

                # ambiguous time, detect whether they mean this evening or
                # the next morning based on whether it has already passed
                if dateNow.hour < HH or (dateNow.hour == HH and
                                         dateNow.minute < MM):
                    pass  # No modification needed
                elif dateNow.hour < HH + 12:
                    HH += 12
                else:
                    # has passed, assume the next morning
                    dayOffset += 1

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

            if wordPrev == "o" or wordPrev == "oh":
                words[words.index(wordPrev)] = ""

            if wordPrev == "early":
                hrOffset = -1
                words[idx - 1] = ""
                idx -= 1
            elif wordPrev == "late":
                hrOffset = 1
                words[idx - 1] = ""
                idx -= 1
            if idx > 0 and wordPrev in markers:
                words[idx - 1] = ""
                if wordPrev == "this":
                    daySpecified = True
            if idx > 1 and wordPrevPrev in markers:
                words[idx - 2] = ""
                if wordPrevPrev == "this":
                    daySpecified = True

            idx += used - 1
            found = True
    # check that we found a date
    if not date_found():
        return None

    if dayOffset is False:
        dayOffset = 0

    # perform date manipulation

    extractedDate = dateNow.replace(microsecond=0)

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
            if not daySpecified and dateNow > extractedDate:
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


def isFractional_en(input_str, short_scale=True):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    if input_str.endswith('s', -1):
        input_str = input_str[:len(input_str) - 1]  # e.g. "fifths"

    fracts = {"whole": 1, "half": 2, "halve": 2, "quarter": 4}
    if short_scale:
        for num in _SHORT_ORDINAL_EN:
            if num > 2:
                fracts[_SHORT_ORDINAL_EN[num]] = num
    else:
        for num in _LONG_ORDINAL_EN:
            if num > 2:
                fracts[_LONG_ORDINAL_EN[num]] = num

    if input_str.lower() in fracts:
        return 1.0 / fracts[input_str.lower()]
    return False


def extract_numbers_en(text, short_scale=True, ordinals=False):
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
    results = _extract_numbers_with_text_en(tokenize(text),
                                            short_scale, ordinals)
    return [float(result.value) for result in results]


class EnglishNormalizer(Normalizer):
    with open(resolve_resource_file("text/en-us/normalize.json")) as f:
        _default_config = json.load(f)


def normalize_en(text, remove_articles):
    """ English string normalization """
    return EnglishNormalizer().normalize(text, remove_articles)


def _date_tokenize_en(date_string):
    date_string = _convert_words_to_numbers_en(date_string, ordinals=True)
    date_string = date_string \
        .replace("a day", "1 day").replace("a month", "1 month") \
        .replace("a week", "1 week").replace("a year", "1 year") \
        .replace("a century", "1 century").replace("a decade", "1 decade")
    words = date_string.split()
    cleaned = ""
    for idx, word in enumerate(words):
        if word == "-":
            word = "minus"
            words[idx] = word
        elif word == "+":
            word = "plus"
            words[idx] = word
        elif word[0] == "-" and word[1].isdigit():
            cleaned += " minus " + word[1:].rstrip(",.!?;:-)/]=}")
        elif word[0] == "+" and word[1].isdigit():
            cleaned += " plus " + word[1:].rstrip(",.!?;:-)/]=}")
        else:
            cleaned += " " + word.rstrip(",.!?;:-)/]=}") \
                .lstrip(",.!?;:-(/[={")
    for n, ordinal in _ORDINAL_BASE_EN.items():
        cleaned = cleaned.replace(ordinal, str(n))
    cleaned = normalize_en(cleaned, remove_articles=True)
    return cleaned.split()


def extract_time_en(time_str, default_time=None,
                    sensitivity=TimeResolution.SECOND):
    default_time = default_time or now_local().time()
    time_qualifiers_am = ['morning']
    time_qualifiers_pm = ['afternoon', 'evening', 'night', 'tonight']
    markers = ['at', 'in', 'on', 'by', 'this', 'around', 'for', 'of', "within"]

    extracted_time = default_time
    time_found = False
    words = _date_tokenize_en(time_str)
    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        word = word.rstrip('s')

    # TODO
    if time_found:
        return extracted_time
    return None


def extract_date_en(date_str, ref_date,
                    resolution=DateResolution.DAY,
                    hemisphere=Hemisphere.NORTH):
    past_qualifiers = ["ago"]
    relative_qualifiers = ["from", "after"]
    relative_past_qualifiers = ["before"]
    of_qualifiers = [
        "of"]  # {ORDINAL} day/week/month.... of month/year/century..
    set_qualifiers = ["is", "was"]  # "the year is 2021"

    more_markers = ["plus", "add", "+"]
    less_markers = ["minus", "subtract", "-"]
    past_markers = ["past", "last"]
    future_markers = ["next"]
    most_recent_qualifiers = ["last"]
    location_markers = ["in", "on", "at", "for"]

    now = ["now"]
    today = ["today"]
    this = ["this", "current", "present"]
    tomorrow = ["tomorrow"]
    yesterday = ["yesterday"]
    day_literal = ["day", "days"]
    week_literal = ["week", "weeks"]
    weekend_literal = ["weekend", "weekends"]
    month_literal = ["month", "months"]
    year_literal = ["year", "years"]
    century_literal = ["century", "centuries"]
    decade_literal = ["decade", "decades"]
    millennium_literal = ["millennium", "millenia", "millenniums"]
    hemisphere_literal = ["hemisphere"]
    season_literal = ["season"]

    date_words = _date_tokenize_en(date_str)

    # check for word boundaries and parse reference dates
    index = 0
    is_relative = False
    is_relative_past = False
    is_past = False
    is_sum = False
    is_subtract = False
    is_of = False
    delta = None

    # is this a negative timespan?
    for marker in past_qualifiers:
        if marker in date_words:
            is_past = True
            index = date_words.index(marker)

    # is this relative to (after) a date?
    for marker in relative_qualifiers:
        if marker in date_words:
            is_relative = True
            index = date_words.index(marker)

    # is this relative to (before) a date?
    for marker in relative_past_qualifiers:
        if marker in date_words:
            is_relative_past = True
            index = date_words.index(marker)

    # is this a timespan in the future?
    for marker in more_markers:
        if marker in date_words:
            is_sum = True
            index = date_words.index(marker)

    # is this a timespan in the past?
    for marker in less_markers:
        if marker in date_words:
            is_subtract = True
            index = date_words.index(marker)

    # cardinal of thing
    # 3rd day of the 4th month of 1994
    for marker in of_qualifiers:
        if marker in date_words:
            is_of = True
            index = date_words.index(marker)

    # parse Nth {X} of Nth {Y}
    if is_of:
        # parse {ORDINAL} day/week/month/year... of {date}
        _ordinal_words = date_words[:index]  # 3rd day / 4th week of the year
        _date_words = date_words[index + 1:]
        _number = None

        _unit = "day"  # TODO is this a sane default ?
        _res = DateResolution.DAY_OF_MONTH

        # parse "{NUMBER} {day/week/month/year...} "
        if len(_ordinal_words) > 1:
            _ordinal = _ordinal_words[-2]
            _unit = _ordinal_words[-1]
            if is_numeric(_ordinal):
                _number = int(_ordinal)
            # parse "last {day/week/month/year...} "
            elif _ordinal_words[0] in most_recent_qualifiers:
                _number = -1

        # parse "{NUMBER}"
        elif len(_ordinal_words) == 1:
            _ordinal = _ordinal_words[0]
            if is_numeric(_ordinal):
                _number = int(_ordinal)

        # parse resolution
        if _number:
            _best_idx = len(_date_words) - 1

            # parse "Nth {day/week/month/year...} of {YEAR}"
            if len(_date_words) and is_numeric(_date_words[0]) \
                    and len(_date_words[0]) == 4:
                ref_date = date(day=1, month=1, year=int(_date_words[0]))
                _res = DateResolution.DAY_OF_YEAR

            # parse "{NUMBER} day
            if _unit in day_literal:
                # parse "{NUMBER} day of month
                for marker in month_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DAY_OF_MONTH
                # parse "{NUMBER} day of year
                for marker in year_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DAY_OF_YEAR
                # parse "{NUMBER} day of decade
                for marker in decade_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DAY_OF_DECADE
                # parse "{NUMBER} day of century
                for marker in century_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DAY_OF_CENTURY
                # parse "{NUMBER} day of millennium
                for marker in millennium_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DAY_OF_MILLENIUM

            # parse "{NUMBER} week
            if _unit in week_literal:
                _res = DateResolution.WEEK_OF_MONTH
                # parse "{NUMBER} week of Nth month
                for marker in month_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.WEEK_OF_MONTH
                # parse "{NUMBER} week of Nth year
                for marker in year_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.WEEK_OF_YEAR
                # parse "{NUMBER} week of Nth decade
                for marker in decade_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.WEEK_OF_DECADE
                # parse "{NUMBER} week of Nth century
                for marker in century_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.WEEK_OF_CENTURY
                # parse "{NUMBER} week of Nth millennium
                for marker in millennium_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.WEEK_OF_MILLENIUM

            # parse "{NUMBER} month
            if _unit in month_literal:
                # parse "{NUMBER} month of Nth year
                _res = DateResolution.MONTH_OF_YEAR
                for marker in year_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.MONTH_OF_YEAR
                # parse "{NUMBER} month of Nth decade
                for marker in decade_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.MONTH_OF_DECADE
                # parse "{NUMBER} month of Nth century
                for marker in century_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        _res = DateResolution.MONTH_OF_CENTURY
                # parse "{NUMBER} month of Nth millenium
                for marker in millennium_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.MONTH_OF_MILLENIUM

            # parse "{NUMBER} year
            if _unit in year_literal:
                _res = DateResolution.YEAR
                for marker in year_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.YEAR
                for marker in decade_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.YEAR_OF_DECADE
                for marker in century_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.YEAR_OF_CENTURY
                for marker in millennium_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.YEAR_OF_MILLENIUM

            # parse "{NUMBER} decade
            if _unit in decade_literal:
                _res = DateResolution.DECADE
                for marker in century_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DECADE_OF_CENTURY
                for marker in millennium_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.DECADE_OF_MILLENIUM

            # parse "{NUMBER} century
            if _unit in century_literal:
                _res = DateResolution.CENTURY
                for marker in millennium_literal:
                    if marker in _date_words:
                        _idx = _date_words.index(marker)
                        if _idx <= _best_idx:
                            _best_idx = _idx
                            _res = DateResolution.CENTURY_OF_MILLENIUM

            # parse "{NUMBER} millennium
            if _unit in millennium_literal:
                _res = DateResolution.MILLENNIUM

        # Calculate Nth of {resolution}
        if _number:
            _date_str = " ".join(_date_words)
            _extracted_date = extract_date_en(_date_str, ref_date,
                                              resolution, hemisphere)
            if not _extracted_date:
                _year = _date_words[0]
                if is_numeric(_year) and len(_year) == 4:
                    _extracted_date = get_ordinal(_year,
                                                  resolution=DateResolution.YEAR)

            if _extracted_date:
                return get_ordinal(_number, _extracted_date, _res)

    # parse {duration} ago
    if is_past:
        # parse {duration} ago
        duration_str = " ".join(date_words[:index])
        delta, remainder = extract_duration_en(duration_str)
        if not delta:
            raise RuntimeError(
                "Could not extract duration from: " + duration_str)

    # parse {duration} after {date}
    if is_relative:
        # parse {duration} from {reference_date}
        # 1 hour 3 minutes from now
        # 5 days from now
        # 3 weeks after tomorrow
        # 5 days before today/tomorrow/tuesday

        duration_str = " ".join(date_words[:index])
        if duration_str:
            delta, remainder = extract_duration_en(duration_str)

            _date_str = " ".join(date_words[index + 1:])
            _extracted_date = extract_date_en(_date_str, ref_date)
            if not _extracted_date and len(date_words) > index + 1:
                _year = date_words[index + 1]
                if len(_year) == 4 and is_numeric(_year):
                    _extracted_date = date(day=1, month=1, year=int(_year))
            return (_extracted_date or ref_date) + delta
        else:
            _date_str = " ".join(date_words[index + 1:])
            _extracted_date = extract_date_en(_date_str, ref_date)
            if not _extracted_date:
                _year = date_words[index + 1]
                if len(_year) == 4 and is_numeric(_year):
                    _extracted_date = date(day=1, month=1, year=int(_year))

            ref_date = _extracted_date or ref_date

            # next day
            if resolution == DateResolution.DAY:
                return ref_date + timedelta(days=1)
            # next week
            elif resolution == DateResolution.WEEK:
                delta = timedelta(weeks=1)
                _extracted_date = ref_date + delta
                _start, _end = get_week_range(_extracted_date)
                return _start
            # next month
            elif resolution == DateResolution.MONTH:
                delta = timedelta(days=31)
                _extracted_date = ref_date + delta
                _start, _end = get_month_range(_extracted_date)
                return _start
            # next year
            elif resolution == DateResolution.YEAR:
                delta = timedelta(days=31 * 12)
                _extracted_date = ref_date + delta
                _start, _end = get_year_range(_extracted_date)
                return _start
            # next decade
            elif resolution == DateResolution.DECADE:
                delta = timedelta(days=366 * 10)
                _extracted_date = ref_date + delta
                _start, _end = get_decade_range(_extracted_date)
                return _start
            # next century
            elif resolution == DateResolution.CENTURY:
                delta = timedelta(days=366 * 100)
                _extracted_date = ref_date + delta
                _start, _end = get_century_range(_extracted_date)
                return _start
            # next millennium
            elif resolution == DateResolution.MILLENNIUM:
                delta = timedelta(days=366 * 1000)
                _extracted_date = ref_date + delta
                _start, _end = get_millennium_range(_extracted_date)
                return _start
            else:
                raise ValueError("Invalid Resolution")

    # parse {duration} before {date}
    if is_relative_past:
        # parse {duration} from {reference_date}
        # 1 hour 3 minutes from now
        # 5 days from now
        # 3 weeks after tomorrow
        # 5 days before today/tomorrow/tuesday

        duration_str = " ".join(date_words[:index])
        if duration_str:
            delta, remainder = extract_duration_en(duration_str)
            _date_str = " ".join(date_words[index + 1:])
            _extracted_date = extract_date_en(_date_str, ref_date)
            if not _extracted_date and len(date_words) > index + 1:
                _year = date_words[index + 1]
                if len(_year) == 4 and is_numeric(_year):
                    _extracted_date = date(day=1, month=1, year=int(_year))
            return (_extracted_date or ref_date) - delta
        else:
            _date_str = " ".join(date_words[index + 1:])
            _extracted_date = extract_date_en(_date_str, ref_date)
            if not _extracted_date:
                _year = date_words[index + 1]
                if len(_year) == 4 and is_numeric(_year):
                    _extracted_date = date(day=1, month=1, year=int(_year))

            ref_date = _extracted_date or ref_date
            # previous day
            if resolution == DateResolution.DAY:
                return ref_date - timedelta(days=1)
            # previous week
            elif resolution == DateResolution.WEEK:
                _extracted_date = ref_date - timedelta(weeks=1)
                _start, _end = get_week_range(_extracted_date)
                return _start
            # previous month
            elif resolution == DateResolution.MONTH:
                delta = timedelta(days=30)
                _extracted_date = ref_date - delta
                _start, _end = get_month_range(_extracted_date)
                return _start
            # previous year
            elif resolution == DateResolution.YEAR:
                delta = timedelta(days=365)
                _extracted_date = ref_date - delta
                _start, _end = get_year_range(_extracted_date)
                return _start
            # previous decade
            elif resolution == DateResolution.DECADE:
                delta = timedelta(days=365 * 10)
                _extracted_date = ref_date - delta
                _start, _end = get_decade_range(ref_date)
                return _start
            # previous century
            elif resolution == DateResolution.CENTURY:
                delta = timedelta(days=365 * 100)
                _extracted_date = ref_date - delta
                _start, _end = get_century_range(ref_date)
                return _start
            # previous millennium
            elif resolution == DateResolution.MILLENNIUM:
                delta = timedelta(days=365 * 1000)
                _extracted_date = ref_date - delta
                _start, _end = get_century_range(ref_date)
                return _start
            else:
                raise ValueError("Invalid Sensitivity")

    # parse {date} plus/minus {duration}
    if is_sum or is_subtract:
        # parse {reference_date} plus {duration}
        # january 5 plus 2 weeks
        # parse {reference_date} minus {duration}
        # now minus 10 days
        duration_str = " ".join(date_words[index + 1:])
        delta, remainder = extract_duration_en(duration_str)

        if not delta:
            raise RuntimeError(
                "Could not extract duration from: " + duration_str)
        _date_str = " ".join(date_words[:index])
        _extracted_date = extract_date_en(_date_str, ref_date)
        if not _extracted_date and len(date_words) > index + 1:
            _year = date_words[index + 1]
            if len(_year) == 4 and is_numeric(_year):
                _extracted_date = date(day=1, month=1, year=int(_year))
        ref_date = _extracted_date or ref_date

    # relative timedelta found
    if delta:
        try:
            if is_past or is_subtract:
                extracted_date = ref_date - delta
            else:
                extracted_date = ref_date + delta
            if isinstance(extracted_date, datetime):
                extracted_date = extracted_date.date()
            return extracted_date
        except OverflowError:
            # TODO how to handle BC dates
            # https://stackoverflow.com/questions/15857797/bc-dates-in-python
            if is_past or is_subtract:
                year_bc = delta.days // 365 - ref_date.year
                bc_str = str(year_bc) + " BC"
                print("ERROR: extracted date is " + bc_str)
            else:
                print("ERROR: extracted date is too far in the future")
            raise

    # iterate the word list to extract a date
    else:
        date_found = False
        extracted_date = ref_date
        extracted_date = extracted_date
        current_date = now_local()
        final_date = False
        for idx, word in enumerate(date_words):
            if final_date:
                break  # no more date updates allowed

            if word == "":
                continue

            wordPrevPrev = date_words[idx - 2] if idx > 1 else ""
            wordPrev = date_words[idx - 1] if idx > 0 else ""
            wordNext = date_words[idx + 1] if idx + 1 < len(date_words) else ""
            wordNextNext = date_words[idx + 2] if idx + 2 < len(
                date_words) else ""
            wordNextNextNext = date_words[idx + 3] if idx + 3 < len(
                date_words) else ""

            # parse "now"
            if word in now:
                date_found = True
                extracted_date = current_date
            # parse "today"
            if word in today:
                date_found = True
                extracted_date = ref_date
            # parse "yesterday"
            if word in yesterday:
                date_found = True
                extracted_date = ref_date - timedelta(days=1)
            # parse "tomorrow"
            if word in tomorrow:
                date_found = True
                extracted_date = ref_date + timedelta(days=1)
            # parse {weekday}
            if weekday_to_int(word, "en"):
                date_found = True
                int_week = weekday_to_int(word, "en")
                _w = extracted_date.weekday()
                _delta = 0
                if wordPrev in past_markers:
                    # parse last {weekday}
                    if int_week == _w:
                        _delta = 7
                    elif int_week < _w:
                        _delta = _w - int_week
                    else:
                        _delta = 7 - int_week + _w
                    extracted_date -= timedelta(days=_delta)
                else:
                    # parse this {weekday}
                    # parse next {weekday}
                    if int_week < _w:
                        _delta = 7 - _w + int_week
                    else:
                        _delta = int_week - _w
                    extracted_date += timedelta(days=_delta)
                assert extracted_date.weekday() == int_week
            # parse {month}
            if month_to_int(word, "en"):
                date_found = True
                int_month = month_to_int(word, "en")

                extracted_date = ref_date.replace(month=int_month, day=1)

                if wordPrev in past_markers:
                    if int_month > ref_date.month:
                        extracted_date = extracted_date.replace(
                            year=ref_date.year - 1)
                elif wordPrev in future_markers:
                    if int_month < ref_date.month:
                        extracted_date = extracted_date.replace(
                            year=ref_date.year + 1)

                if is_numeric(wordNext) and 0 < int(wordNext) <= 31:
                    # parse {month} {DAY_OF_MONTH}
                    extracted_date = extracted_date.replace(day=int(wordNext))
                    # parse {month} {DAY_OF_MONTH} {YYYY}
                    if len(wordNextNext) == 4 and is_numeric(wordNextNext):
                        extracted_date = extracted_date \
                            .replace(year=int(wordNextNext))

                elif is_numeric(wordPrev):
                    # parse {DAY_OF_MONTH} {month}
                    extracted_date = extracted_date.replace(day=int(wordPrev))

                if is_numeric(wordNext) and len(wordNext) == 4:
                    # parse {month} {YEAR}
                    extracted_date = extracted_date.replace(year=int(wordNext))
                elif is_numeric(wordPrev) and len(wordPrev) == 4:
                    # parse {YEAR} {month}
                    extracted_date = extracted_date.replace(year=int(wordPrev))
            # parse "season"
            if word in season_literal:
                _start, _end = get_season_range(ref_date,
                                                hemisphere=hemisphere)
                # parse "in {Number} seasons"
                if is_numeric(wordPrev):
                    date_found = True
                    raise NotImplementedError
                # parse "this season"
                elif wordPrev in this:
                    date_found = True
                    extracted_date = _start
                # parse "last season"
                elif wordPrev in past_markers:
                    date_found = True
                    _end = _start - timedelta(days=2)
                    s = date_to_season(_end, hemisphere)
                    extracted_date = last_season_date(s, ref_date, hemisphere)
                # parse "next season"
                elif wordPrev in future_markers:
                    date_found = True
                    extracted_date = _end + timedelta(days=1)
            # parse "spring"
            if word in _SEASONS_EN[Season.SPRING]:
                date_found = True
                # parse "in {Number} springs"
                if is_numeric(wordPrev):
                    raise NotImplementedError
                # parse "last spring"
                elif wordPrev in past_markers:
                    extracted_date = last_season_date(Season.SPRING,
                                                      ref_date,
                                                      hemisphere)
                # parse "next spring"
                elif wordPrev in future_markers:
                    extracted_date = next_season_date(Season.SPRING,
                                                      ref_date,
                                                      hemisphere)
                else:
                    # parse "[this] spring"
                    extracted_date = season_to_date(Season.SPRING,
                                                    ref_date,
                                                    hemisphere)
            # parse "fall"
            if word in _SEASONS_EN[Season.FALL]:
                date_found = True
                # parse "in {Number} falls"
                if is_numeric(wordPrev):
                    raise NotImplementedError
                # parse "last fall"
                elif wordPrev in past_markers:
                    extracted_date = last_season_date(Season.FALL, ref_date,
                                                      hemisphere)
                # parse "next fall"
                elif wordPrev in future_markers:
                    extracted_date = next_season_date(Season.FALL, ref_date,
                                                      hemisphere)
                # parse "[this] fall"
                else:
                    extracted_date = season_to_date(Season.FALL,
                                                    ref_date,
                                                    hemisphere)
            # parse "summer"
            if word in _SEASONS_EN[Season.SUMMER]:
                date_found = True
                # parse "in {Number} summers"
                if is_numeric(wordPrev):
                    raise NotImplementedError
                # parse "last summer"
                elif wordPrev in past_markers:
                    extracted_date = last_season_date(Season.SUMMER, ref_date,
                                                      hemisphere)
                # parse "next summer"
                elif wordPrev in future_markers:
                    extracted_date = next_season_date(Season.SUMMER, ref_date,
                                                      hemisphere)
                # parse "[this] summer"
                else:
                    extracted_date = season_to_date(Season.SUMMER,
                                                    ref_date,
                                                    hemisphere)
            # parse "winter"
            if word in _SEASONS_EN[Season.WINTER]:
                date_found = True
                # parse "in {Number} winters"
                if is_numeric(wordPrev):
                    raise NotImplementedError
                # parse "last winter"
                elif wordPrev in past_markers:
                    extracted_date = last_season_date(Season.WINTER, ref_date,
                                                      hemisphere)
                # parse "next winter"
                elif wordPrev in future_markers:
                    extracted_date = next_season_date(Season.WINTER, ref_date,
                                                      hemisphere)
                # parse "[this] winter"
                else:
                    extracted_date = season_to_date(Season.WINTER,
                                                    ref_date,
                                                    hemisphere)
            # parse "day"
            if word in day_literal:
                # parse {ORDINAL} day
                if is_numeric(wordPrev):
                    date_found = True
                    extracted_date = extracted_date.replace(day=int(wordPrev))
                # parse day {NUMBER}
                elif is_numeric(wordNext):
                    date_found = True
                    extracted_date = extracted_date.replace(day=int(wordNext))
                # parse "present day"
                elif wordPrev in this:
                    date_found = True
                    extracted_date = ref_date
            # parse "weekend"
            if word in weekend_literal:
                _is_weekend = ref_date.weekday() >= 5
                # parse {ORDINAL} weekend
                if is_numeric(wordPrev):
                    date_found = True
                    raise NotImplementedError
                # parse weekend {NUMBER}
                elif is_numeric(wordNext):
                    date_found = True
                    raise NotImplementedError
                # parse "this weekend"
                elif wordPrev in this:
                    date_found = True
                    _start, _end = get_weekend_range(ref_date)
                    extracted_date = _start
                # parse "next weekend"
                elif wordPrev in future_markers:
                    date_found = True
                    if not _is_weekend:
                        _start, _end = get_weekend_range(ref_date)
                    else:
                        _start, _end = get_weekend_range(ref_date +
                                                         timedelta(weeks=1))
                    extracted_date = _start
                # parse "last weekend"
                elif wordPrev in past_markers:
                    date_found = True
                    _start, _end = get_weekend_range(ref_date -
                                                     timedelta(weeks=1))
                    extracted_date = _start
            # parse "week"
            if word in week_literal:
                # parse {ORDINAL} week
                if is_numeric(wordPrev) and 0 < int(wordPrev) <= 4 * 12:
                    date_found = True
                    extracted_date = get_ordinal(int(wordPrev), ref_date,
                                                 resolution=DateResolution.WEEK_OF_YEAR)
                # parse "this week"
                if wordPrev in this:
                    date_found = True
                    _start, _end = get_week_range(ref_date)
                    extracted_date = _start
                # parse "last week"
                elif wordPrev in past_markers:
                    date_found = True
                    _last_week = ref_date - timedelta(weeks=1)
                    _start, _end = get_week_range(_last_week)
                    extracted_date = _start
                # parse "next week"
                elif wordPrev in future_markers:
                    date_found = True
                    _last_week = ref_date + timedelta(weeks=1)
                    _start, _end = get_week_range(_last_week)
                    extracted_date = _start
                # parse week {NUMBER}
                elif is_numeric(wordNext) and 0 < int(wordNext) <= 12:
                    date_found = True
                    extracted_date = get_ordinal(int(wordNext), ref_date,
                                                 resolution=DateResolution.WEEK_OF_YEAR)
            # parse "month"
            if word in month_literal:

                # parse {ORDINAL} month
                if is_numeric(wordPrev) and 0 < int(wordPrev) <= 12:
                    date_found = True
                    extracted_date = get_ordinal(int(wordPrev), ref_date,
                                                 DateResolution.MONTH_OF_YEAR)
                # parse month {NUMBER}
                elif is_numeric(wordNext) and 0 < int(wordNext) <= 12:
                    date_found = True
                    extracted_date = get_ordinal(int(wordNext), ref_date,
                                                 DateResolution.MONTH_OF_YEAR)
                # parse "this month"
                elif wordPrev in this:
                    date_found = True
                    extracted_date = ref_date.replace(day=1)
                # parse "next month"
                elif wordPrev in future_markers:
                    date_found = True
                    _next_month = ref_date + timedelta(days=30)
                    extracted_date = _next_month.replace(day=1)
                # parse "last month"
                elif wordPrev in past_markers:
                    date_found = True
                    _last_month = ref_date - timedelta(days=30)
                    extracted_date = _last_month.replace(day=1)
            # parse "year"
            if word in year_literal:
                # parse "current year"
                if wordPrev in this:
                    date_found = True
                    extracted_date = get_ordinal(ref_date.year,
                                                 resolution=DateResolution.YEAR)
                # parse "last year"
                elif wordPrev in past_markers:
                    date_found = True
                    extracted_date = get_ordinal(ref_date.year - 1,
                                                 resolution=DateResolution.YEAR)
                # parse "next year"
                elif wordPrev in future_markers:
                    date_found = True
                    extracted_date = get_ordinal(ref_date.year + 1,
                                                 resolution=DateResolution.YEAR)
                # parse Nth year
                elif is_numeric(wordPrev):
                    date_found = True
                    extracted_date = get_ordinal(int(wordPrev) - 1,
                                                 resolution=DateResolution.YEAR)
            # parse "decade"
            if word in decade_literal:
                _decade = (ref_date.year // 10) + 1
                # parse "current decade"
                if wordPrev in this:
                    date_found = True
                    extracted_date = get_ordinal(_decade,
                                                 resolution=DateResolution.DECADE)
                # parse "last decade"
                elif wordPrev in past_markers:
                    date_found = True
                    extracted_date = get_ordinal(_decade - 1,
                                                 resolution=DateResolution.DECADE)
                # parse "next decade"
                elif wordPrev in future_markers:
                    date_found = True
                    extracted_date = get_ordinal(_decade + 1,
                                                 resolution=DateResolution.DECADE)
                # parse Nth decade
                elif is_numeric(wordPrev):
                    date_found = True
                    extracted_date = get_ordinal(int(wordPrev),
                                                 resolution=DateResolution.DECADE)
            # parse "millennium"
            if word in millennium_literal:
                _mil = ref_date.year // 1000
                # parse "current millennium"
                if wordPrev in this:
                    date_found = True
                    extracted_date = get_ordinal(_mil, ref_date,
                                                 DateResolution.MILLENNIUM)
                # parse "last millennium"
                elif wordPrev in past_markers:
                    date_found = True
                    extracted_date = get_ordinal(_mil - 1, ref_date,
                                                 DateResolution.MILLENNIUM)
                # parse "next millennium"
                elif wordPrev in future_markers:
                    date_found = True
                    extracted_date = get_ordinal(_mil + 1, ref_date,
                                                 DateResolution.MILLENNIUM)
                # parse Nth millennium
                elif is_numeric(wordPrev):
                    date_found = True

                    extracted_date = get_ordinal(int(wordPrev) - 1,
                                                 extracted_date,
                                                 DateResolution.MILLENNIUM)
            # parse "century"
            if word in century_literal:
                _century = ref_date.year // 100
                # parse "current century"
                if wordPrev in this:
                    date_found = True
                    extracted_date = get_ordinal(_century, ref_date,
                                                 DateResolution.CENTURY)
                # parse "last century"
                elif wordPrev in past_markers:
                    date_found = True
                    extracted_date = get_ordinal(_century - 1,
                                                 ref_date,
                                                 DateResolution.CENTURY)
                # parse "next century"
                elif wordPrev in future_markers:
                    date_found = True
                    extracted_date = get_ordinal(_century + 1,
                                                 ref_date,
                                                 DateResolution.CENTURY)
                # parse Nth century
                elif is_numeric(wordPrev):
                    date_found = True

                    extracted_date = get_ordinal(int(wordPrev) - 1,
                                                 extracted_date,
                                                 DateResolution.CENTURY)
            # parse day/mont/year is NUMBER
            if word in set_qualifiers and is_numeric(wordNext):
                _ordinal = int(wordNext)
                if wordPrev in day_literal:
                    date_found = True
                    extracted_date = get_ordinal(_ordinal, extracted_date,
                                                 DateResolution.DAY_OF_MONTH)
                elif wordPrev in month_literal:
                    date_found = True
                    extracted_date = get_ordinal(_ordinal, extracted_date,
                                                 DateResolution.MONTH_OF_YEAR)
                elif wordPrev in year_literal:
                    date_found = True
                    extracted_date = get_ordinal(_ordinal, extracted_date,
                                                 DateResolution.YEAR)
                elif wordPrev in decade_literal:
                    date_found = True
                    extracted_date = get_ordinal(_ordinal, extracted_date,
                                                 DateResolution.DECADE)
                elif wordPrev in century_literal:
                    date_found = True
                    extracted_date = get_ordinal(_ordinal, extracted_date,
                                                 DateResolution.CENTURY)
                elif wordPrev in millennium_literal:
                    date_found = True
                    extracted_date = get_ordinal(_ordinal, extracted_date,
                                                 DateResolution.MILLENNIUM)
                # TODO week of month vs week of year
            # parse {date} at {location}
            if word in location_markers:
                # this is used to parse seasons, which depend on
                # geographical location
                # "i know what you did last summer",  "winter is coming"
                # usually the default will be set automatically based on user
                # location

                # parse {date} at north hemisphere
                if wordNext in _HEMISPHERES_EN[Hemisphere.NORTH] and \
                        wordNextNext in hemisphere_literal:
                    hemisphere = Hemisphere.NORTH
                # parse {date} at south hemisphere
                elif wordNext in _HEMISPHERES_EN[Hemisphere.SOUTH] and \
                        wordNextNext in hemisphere_literal:
                    hemisphere = Hemisphere.SOUTH
                # parse {date} at {country/city}
                elif _ner is not None:
                    # parse string for Country names
                    for r in _ner.extract_entities(wordNext):
                        if r.entity_type == "Country":
                            if r.data["latitude"] < 0:
                                hemisphere = Hemisphere.SOUTH
                            else:
                                hemisphere = Hemisphere.NORTH
                    else:
                        #  or Capital city names
                        for r in _ner.extract_entities(wordNext):
                            if r.entity_type == "Capital City":
                                if r.data["hemisphere"].startswith("s"):
                                    hemisphere = Hemisphere.SOUTH
                                else:
                                    hemisphere = Hemisphere.NORTH

    if date_found:
        if isinstance(extracted_date, datetime):
            extracted_date = extracted_date.date()
        return extracted_date
    return None
