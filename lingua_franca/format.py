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

from os.path import join

from lingua_franca.lang import get_full_lang_code, get_primary_lang_code

from lingua_franca.lang.format_en import *
from lingua_franca.lang.format_pt import *
from lingua_franca.lang.format_it import *
from lingua_franca.lang.format_sv import *
from lingua_franca.lang.format_hu import *

from lingua_franca.lang.format_es import nice_number_es
from lingua_franca.lang.format_es import nice_time_es
from lingua_franca.lang.format_es import pronounce_number_es
from lingua_franca.lang.format_de import nice_number_de
from lingua_franca.lang.format_de import nice_time_de
from lingua_franca.lang.format_de import pronounce_number_de
from lingua_franca.lang.format_fr import nice_number_fr
from lingua_franca.lang.format_fr import nice_time_fr
from lingua_franca.lang.format_fr import pronounce_number_fr
from lingua_franca.lang.format_nl import nice_time_nl
from lingua_franca.lang.format_nl import pronounce_number_nl
from lingua_franca.lang.format_nl import nice_number_nl
from lingua_franca.lang.format_da import nice_number_da
from lingua_franca.lang.format_da import nice_time_da
from lingua_franca.lang.format_da import pronounce_number_da

from lingua_franca.bracket_expansion import SentenceTreeParser
from lingua_franca import _log_unsupported_language

from quantulum3 import parser as quantity_parser

from collections import namedtuple
import json
import os
import datetime
import re


def _translate_word(name, lang):
    """ Helper to get word tranlations

    Args:
        name (str): Word name. Returned as the default value if not translated.
        lang (str): Language code, e.g. "en-us"

    Returns:
        str: translated version of resource name
    """
    from lingua_franca import resolve_resource_file

    lang_code = get_full_lang_code(lang)

    filename = resolve_resource_file(join("text", lang_code, name+".word"))
    if filename:
        # open the file
        try:
            with open(filename, 'r', encoding='utf8') as f:
                for line in f:
                    word = line.strip()
                    if word.startswith("#"):
                        continue  # skip comment lines
                    return word
        except Exception:
            pass
    return name  # use resource name as the word


NUMBER_TUPLE = namedtuple(
    'number',
    ('x, xx, x0, x_in_x0, xxx, x00, x_in_x00, xx00, xx_in_xx00, x000, ' +
     'x_in_x000, x0_in_x000, x_in_0x00'))


class DateTimeFormat:
    def __init__(self, config_path):
        self.lang_config = {}
        self.config_path = config_path

    def cache(self, lang):
        if lang not in self.lang_config:
            try:
                # Attempt to load the language-specific formatting data
                with open(self.config_path + '/' + lang + '/date_time.json',
                          'r') as lang_config_file:
                    self.lang_config[lang] = json.loads(
                        lang_config_file.read())
            except FileNotFoundError:
                # Fallback to English formatting
                with open(self.config_path + '/en-us/date_time.json',
                          'r') as lang_config_file:
                    self.lang_config[lang] = json.loads(
                        lang_config_file.read())

            for x in ['decade_format', 'hundreds_format', 'thousand_format',
                      'year_format']:
                i = 1
                while self.lang_config[lang][x].get(str(i)):
                    self.lang_config[lang][x][str(i)]['re'] = (
                        re.compile(self.lang_config[lang][x][str(i)]['match']
                                   ))
                    i = i + 1

    def _number_strings(self, number, lang):
        x = (self.lang_config[lang]['number'].get(str(number % 10)) or
             str(number % 10))
        xx = (self.lang_config[lang]['number'].get(str(number % 100)) or
              str(number % 100))
        x_in_x0 = self.lang_config[lang]['number'].get(
            str(int(number % 100 / 10))) or str(int(number % 100 / 10))
        x0 = (self.lang_config[lang]['number'].get(
            str(int(number % 100 / 10) * 10)) or
              str(int(number % 100 / 10) * 10))
        xxx = (self.lang_config[lang]['number'].get(str(number % 1000)) or
               str(number % 1000))
        x00 = (self.lang_config[lang]['number'].get(str(int(
            number % 1000 / 100) * 100)) or
               str(int(number % 1000 / 100) * 100))
        x_in_x00 = self.lang_config[lang]['number'].get(str(int(
            number % 1000 / 100))) or str(int(number % 1000 / 100))
        xx00 = self.lang_config[lang]['number'].get(str(int(
            number % 10000 / 100) * 100)) or str(int(number % 10000 / 100) *
                                                 100)
        xx_in_xx00 = self.lang_config[lang]['number'].get(str(int(
            number % 10000 / 100))) or str(int(number % 10000 / 100))
        x000 = (self.lang_config[lang]['number'].get(str(int(
            number % 10000 / 1000) * 1000)) or
                str(int(number % 10000 / 1000) * 1000))
        x_in_x000 = self.lang_config[lang]['number'].get(str(int(
            number % 10000 / 1000))) or str(int(number % 10000 / 1000))
        x0_in_x000 = self.lang_config[lang]['number'].get(str(int(
            number % 10000 / 1000)*10)) or str(int(number % 10000 / 1000)*10)
        x_in_0x00 = self.lang_config[lang]['number'].get(str(int(
            number % 1000 / 100)) or str(int(number % 1000 / 100)))

        return NUMBER_TUPLE(
            x, xx, x0, x_in_x0, xxx, x00, x_in_x00, xx00, xx_in_xx00, x000,
            x_in_x000, x0_in_x000, x_in_0x00)

    def _format_string(self, number, format_section, lang):
        s = self.lang_config[lang][format_section]['default']
        i = 1
        while self.lang_config[lang][format_section].get(str(i)):
            e = self.lang_config[lang][format_section][str(i)]
            if e['re'].match(str(number)):
                return e['format']
            i = i + 1
        return s

    def _decade_format(self, number, number_tuple, lang):
        s = self._format_string(number % 100, 'decade_format', lang)
        return s.format(x=number_tuple.x, xx=number_tuple.xx,
                        x0=number_tuple.x0, x_in_x0=number_tuple.x_in_x0,
                        number=str(number % 100))

    def _number_format_hundreds(self, number, number_tuple, lang,
                                formatted_decade):
        s = self._format_string(number % 1000, 'hundreds_format', lang)
        return s.format(xxx=number_tuple.xxx, x00=number_tuple.x00,
                        x_in_x00=number_tuple.x_in_x00,
                        formatted_decade=formatted_decade,
                        number=str(number % 1000))

    def _number_format_thousand(self, number, number_tuple, lang,
                                formatted_decade, formatted_hundreds):
        s = self._format_string(number % 10000, 'thousand_format', lang)
        return s.format(x_in_x00=number_tuple.x_in_x00,
                        xx00=number_tuple.xx00,
                        xx_in_xx00=number_tuple.xx_in_xx00,
                        x000=number_tuple.x000,
                        x_in_x000=number_tuple.x_in_x000,
                        x0_in_x000=number_tuple.x0_in_x000,
                        x_in_0x00=number_tuple.x_in_0x00,
                        formatted_decade=formatted_decade,
                        formatted_hundreds=formatted_hundreds,
                        number=str(number % 10000))

    def date_format(self, dt, lang, now):
        format_str = 'date_full'
        if now:
            if dt.year == now.year:
                format_str = 'date_full_no_year'
                if dt.month == now.month and dt.day > now.day:
                    format_str = 'date_full_no_year_month'

            tomorrow = now + datetime.timedelta(days=1)
            yesterday = now - datetime.timedelta(days=1)
            if tomorrow.date() == dt.date():
                format_str = 'tomorrow'
            elif now.date() == dt.date():
                format_str = 'today'
            elif yesterday.date() == dt.date():
                format_str = 'yesterday'

        return self.lang_config[lang]['date_format'][format_str].format(
            weekday=self.lang_config[lang]['weekday'][str(dt.weekday())],
            month=self.lang_config[lang]['month'][str(dt.month)],
            day=self.lang_config[lang]['date'][str(dt.day)],
            formatted_year=self.year_format(dt, lang, False))

    def date_time_format(self, dt, lang, now, use_24hour, use_ampm):
        date_str = self.date_format(dt, lang, now)
        time_str = nice_time(dt, lang, use_24hour=use_24hour,
                             use_ampm=use_ampm)
        return self.lang_config[lang]['date_time_format']['date_time'].format(
            formatted_date=date_str, formatted_time=time_str)

    def year_format(self, dt, lang, bc):
        number_tuple = self._number_strings(dt.year, lang)
        formatted_bc = (
            self.lang_config[lang]['year_format']['bc'] if bc else '')
        formatted_decade = self._decade_format(
            dt.year, number_tuple, lang)
        formatted_hundreds = self._number_format_hundreds(
            dt.year, number_tuple, lang, formatted_decade)
        formatted_thousand = self._number_format_thousand(
            dt.year, number_tuple, lang, formatted_decade, formatted_hundreds)

        s = self._format_string(dt.year, 'year_format', lang)

        return re.sub(' +', ' ',
                      s.format(
                          year=str(dt.year),
                          century=str(int(dt.year / 100)),
                          decade=str(dt.year % 100),
                          formatted_hundreds=formatted_hundreds,
                          formatted_decade=formatted_decade,
                          formatted_thousand=formatted_thousand,
                          bc=formatted_bc)).strip()


date_time_format = DateTimeFormat(os.path.join(os.path.dirname(__file__),
                                  'res/text'))


def nice_unit(unit=None, context=None, lang=None):
    """
        Format a unit to a pronouncable string
        Args:
            unit (string): The unit abbreviation that is to be pronounced
                (i.e. "C", "MW", "mW", "°F" etc)
            context (string): A text in which the correct meaning of this
                abbreviation becomes clear (i.e. "It's almost 30 C outside")
                If given, the whole context will be parsed and the first unit
                to be found returned
            lang (string): the language to use, use Mycroft default language if
                not provided
        Returns:
            (str): A fully de-abbreviated unit for insertion in a context like
                    situation (i.e. "degree Celsius", "percent")
            (object): The parsed value of the quantity, if any (else None)
    """
    lang = get_primary_lang_code(lang)
    # Return an empty string for None and empty strings
    if not unit and not context:
        return ''
    try:
        # Quantulum expects a unit to be prefixed with a quantifier
        quantity = quantity_parser.parse(
            context or "1 {}".format(unit),
            lang
        )
        if len(quantity) > 0:
            quantity = quantity[0]
            return (
                quantity.unit.to_spoken(quantity.value, lang),
                quantity.value if context else None
            )
        else:
            return unit, None
    except NotImplementedError:
        return unit, None


def expand_units(text, lang=None):
    """
        Format all units in a text and their amount into pronouncable strings
        Args:
            text (string): A text, ideally containing compact units
                            (i.e. "It's almost 30 C outside")
            lang (string): the language to use, use Mycroft default language if
                not provided
        Returns:
            (str): A text with fully de-abbreviated units
    """
    lang = get_primary_lang_code(lang)
    try:
        return quantity_parser.inline_parse_and_expand(text, lang)
    except NotImplementedError:
        return text


def nice_number(number, lang=None, speech=True, denominators=None):
    """Format a float to human readable functions

    This function formats a float to human understandable functions. Like
    4.5 becomes 4 and a half for speech and 4 1/2 for text
    Args:
        number (int or float): the float to format
        lang (str): code for the language to use
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """
    # Convert to spoken representation in appropriate language
    lang_code = get_primary_lang_code(lang)
    if lang_code == "en":
        return nice_number_en(number, speech, denominators)
    elif lang_code == "es":
        return nice_number_es(number, speech, denominators)
    elif lang_code == "pt":
        return nice_number_pt(number, speech, denominators)
    elif lang_code == "it":
        return nice_number_it(number, speech, denominators)
    elif lang_code == "fr":
        return nice_number_fr(number, speech, denominators)
    elif lang_code == "sv":
        return nice_number_sv(number, speech, denominators)
    elif lang_code == "de":
        return nice_number_de(number, speech, denominators)
    elif lang_code == "hu":
        return nice_number_hu(number, speech, denominators)
    elif lang_code == "nl":
        return nice_number_nl(number, speech, denominators)
    elif lang_code == "da":
        return nice_number_da(number, speech, denominators)

    # Default to the raw number for unsupported languages,
    # hopefully the STT engine will pronounce understandably.
    # TODO: nice_number_XX for other languages
    _log_unsupported_language(lang_code, ['en', 'es', 'pt', 'it', 'fr',
                                          'sv', 'de', 'hu', 'nl', 'da'])
    return str(number)


def nice_time(dt, lang=None, speech=True, use_24hour=False,
              use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'five thirty' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        lang (str): code for the language to use
        speech (bool): format for speech (default/True) or display (False)
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    lang_code = get_primary_lang_code(lang)
    if lang_code == "en":
        return nice_time_en(dt, speech, use_24hour, use_ampm)
    elif lang_code == "es":
        return nice_time_es(dt, speech, use_24hour, use_ampm)
    elif lang_code == "it":
        return nice_time_it(dt, speech, use_24hour, use_ampm)
    elif lang_code == "fr":
        return nice_time_fr(dt, speech, use_24hour, use_ampm)
    elif lang_code == "de":
        return nice_time_de(dt, speech, use_24hour, use_ampm)
    elif lang_code == "hu":
        return nice_time_hu(dt, speech, use_24hour, use_ampm)
    elif lang_code == "nl":
        return nice_time_nl(dt, speech, use_24hour, use_ampm)
    elif lang_code == "da":
        return nice_time_da(dt, speech, use_24hour, use_ampm)
    elif lang_code == "pt":
        return nice_time_pt(dt, speech, use_24hour, use_ampm)

    # TODO: Other languages
    _log_unsupported_language(lang_code, ['en', 'es', 'pt', 'it', 'fr',
                                          'de', 'hu', 'nl', 'da'])
    return str(dt)


def pronounce_number(number, lang=None, places=2, short_scale=True,
                     scientific=False, ordinals=False):
    """
    Convert a number to it's spoken equivalent

    For example, '5' would be 'five'

    Args:
        number: the number to pronounce
        short_scale (bool) : use short (True) or long scale (False)
            https://en.wikipedia.org/wiki/Names_of_large_numbers
        scientific (bool) : convert and pronounce in scientific notation
        ordinals (bool): pronounce in ordinal form "first" instead of "one"
    Returns:
        (str): The pronounced number
    """
    lang_code = get_primary_lang_code(lang)
    if lang_code == "en":
        return pronounce_number_en(number, places=places,
                                   short_scale=short_scale,
                                   scientific=scientific,
                                   ordinals=ordinals)
    elif lang_code == "it":
        return pronounce_number_it(number, places=places,
                                   short_scale=short_scale,
                                   scientific=scientific)
    elif lang_code == "es":
        return pronounce_number_es(number, places=places)
    elif lang_code == "fr":
        return pronounce_number_fr(number, places=places)
    elif lang_code == "de":
        return pronounce_number_de(number, places=places)
    elif lang_code == "hu":
        return pronounce_number_hu(number, places=places)
    elif lang_code == "nl":
        return pronounce_number_nl(number, places=places)
    elif lang_code == "da":
        return pronounce_number_da(number, places=places)
    elif lang_code == "pt":
        return pronounce_number_pt(number, places=places)

    # Default to just returning the numeric value
    # TODO: Other languages
    _log_unsupported_language(lang_code, ['en', 'es', 'pt', 'it', 'fr',
                                          'de', 'hu', 'nl', 'da'])
    return str(number)


def nice_date(dt, lang=None, now=None):
    """
    Format a datetime to a pronounceable date

    For example, generates 'tuesday, june the fifth, 2018'
    Args:
        dt (datetime): date to format (assumes already in local timezone)
        lang (string): the language to use, use Mycroft default language if not
            provided
        now (datetime): Current date. If provided, the returned date for speech
            will be shortened accordingly: No year is returned if now is in the
            same year as td, no month is returned if now is in the same month
            as td. If now and td is the same day, 'today' is returned.
    Returns:
        (str): The formatted date string
    """
    full_code = get_full_lang_code(lang)
    date_time_format.cache(full_code)

    return date_time_format.date_format(dt, full_code, now)


def nice_date_time(dt, lang=None, now=None, use_24hour=False,
                   use_ampm=False):
    """
        Format a datetime to a pronounceable date and time

        For example, generate 'tuesday, june the fifth, 2018 at five thirty'

        Args:
            dt (datetime): date to format (assumes already in local timezone)
            lang (string): the language to use, use Mycroft default language if
                not provided
            now (datetime): Current date. If provided, the returned date for
                speech will be shortened accordingly: No year is returned if
                now is in the same year as td, no month is returned if now is
                in the same month as td. If now and td is the same day, 'today'
                is returned.
            use_24hour (bool): output in 24-hour/military or 12-hour format
            use_ampm (bool): include the am/pm for 12-hour format
        Returns:
            (str): The formatted date time string
    """

    full_code = get_full_lang_code(lang)
    date_time_format.cache(full_code)

    return date_time_format.date_time_format(dt, full_code, now, use_24hour,
                                             use_ampm)


def nice_year(dt, lang=None, bc=False):
    """
        Format a datetime to a pronounceable year

        For example, generate 'nineteen-hundred and eighty-four' for year 1984

        Args:
            dt (datetime): date to format (assumes already in local timezone)
            lang (string): the language to use, use Mycroft default language if
            not provided
            bc (bool) pust B.C. after the year (python does not support dates
                B.C. in datetime)
        Returns:
            (str): The formatted year string
    """

    full_code = get_full_lang_code(lang)
    date_time_format.cache(full_code)

    return date_time_format.year_format(dt, full_code, bc)


def nice_duration(duration, lang=None, speech=True):
    """ Convert duration in seconds to a nice spoken timespan

    Examples:
       duration = 60  ->  "1:00" or "one minute"
       duration = 163  ->  "2:43" or "two minutes forty three seconds"

    Args:
        duration: time, in seconds
        lang (str, optional): a BCP-47 language code, None for default
        speech (bool): format for speech (True) or display (False)
    Returns:
        str: timespan as a string
    """
    if type(duration) is datetime.datetime:
        duration = duration - datetime.datetime.now()
    if type(duration) is datetime.timedelta:
        duration = abs(duration.total_seconds())

    # Do traditional rounding: 2.5->3, 3.5->4, plus this
    # helps in a few cases of where calculations generate
    # times like 2:59:59.9 instead of 3:00.
    duration += 0.5

    days = int(duration // 86400)
    hours = int(duration // 3600 % 24)
    minutes = int(duration // 60 % 60)
    seconds = int(duration % 60)

    if speech:
        out = ""
        if days > 0:
            out += pronounce_number(days, lang) + " "
            if days == 1:
                out += _translate_word("day", lang)
            else:
                out += _translate_word("days", lang)
            out += " "
        if hours > 0:
            if out:
                out += " "
            out += pronounce_number(hours, lang) + " "
            if hours == 1:
                out += _translate_word("hour", lang)
            else:
                out += _translate_word("hours", lang)
        if minutes > 0:
            if out:
                out += " "
            out += pronounce_number(minutes, lang) + " "
            if minutes == 1:
                out += _translate_word("minute", lang)
            else:
                out += _translate_word("minutes", lang)
        if seconds > 0:
            if out:
                out += " "
            out += pronounce_number(seconds, lang) + " "
            if seconds == 1:
                out += _translate_word("second", lang)
            else:
                out += _translate_word("seconds", lang)
    else:
        # M:SS, MM:SS, H:MM:SS, Dd H:MM:SS format
        out = ""
        if days > 0:
            out = str(days) + "d "
        if hours > 0 or days > 0:
            out += str(hours) + ":"
        if minutes < 10 and (hours > 0 or days > 0):
            out += "0"
        out += str(minutes)+":"
        if seconds < 10:
            out += "0"
        out += str(seconds)

    return out


def join_list(items, connector, sep=None, lang=None):
    """ Join a list into a phrase using the given connector word

    Examples:
        join_list([1,2,3], "and") ->  "1, 2 and 3"
        join_list([1,2,3], "and", ";") ->  "1; 2 and 3"

    Args:
        items(array): items to be joined
        connector(str): connecting word (resource name), like "and" or "or"
        sep(str, optional): separator character, default = ","
    Returns:
        str: the connected list phrase
    """

    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])

    if not sep:
        sep = ", "
    else:
        sep += " "
    return (sep.join(str(item) for item in items[:-1]) +
            " " + _translate_word(connector, lang) +
            " " + items[-1])


def expand_parentheses(sent):
    """
    ['1', '(', '2', '|', '3, ')'] -> [['1', '2'], ['1', '3']]
    For example:
    Will it (rain|pour) (today|tomorrow|)?
    ---->
    Will it rain today?
    Will it rain tomorrow?
    Will it rain?
    Will it pour today?
    Will it pour tomorrow?
    Will it pour?
    Args:
        sent (list<str>): List of tokens in sentence
    Returns:
        list<list<str>>: Multiple possible sentences from original
    """
    return SentenceTreeParser(sent).expand_parentheses()


def expand_options(parentheses_line: str) -> list:
    """
    Convert 'test (a|b)' -> ['test a', 'test b']
    Args:
        parentheses_line: Input line to expand
    Returns:
        List of expanded possibilities
    """
    # 'a(this|that)b' -> [['a', 'this', 'b'], ['a', 'that', 'b']]
    options = expand_parentheses(re.split(r'([(|)])', parentheses_line))
    return [re.sub(r'\s+', ' ', ' '.join(i)).strip() for i in options]
