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
import datetime

from lingua_franca.lang.format_common import convert_to_mixed_fraction
from lingua_franca.lang.common_data_fa import _NUM_STRING_FA, \
    _FRACTION_STRING_FA, _SCALE_FA, _ORDINAL_FA, _DECIMAL_STRING_FA


def nice_number_fa(number, speech=True, denominators=range(1, 21)):
    """ Farsi helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "چهار و نیم" for speech and "4 1/2" for text

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
    den_str = _FRACTION_STRING_FA[den]
    if whole == 0:
        if den == 2:
            return 'نیم'
        return_string = '{} {}'.format(num, den_str)
    else:
        if den == 2:
            return '{} و نیم'.format(whole)
        return_string = '{} و {} {}'.format(whole, num, den_str)
    return return_string


def pronounce_number_fa(number, places=2, short_scale=True, scientific=False,
                        ordinals=False):
    """
    Convert a number to it's spoken equivalent

    For example, '5.2' would return 'پنج و دو دهم'

    Args:
        num(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
        short_scale (bool) : use short (True) or long scale (False)
            https://en.wikipedia.org/wiki/Names_of_large_numbers
        scientific (bool): pronounce in scientific notation
        ordinals (bool): pronounce in ordinal form "first" instead of "one"
    Returns:
        (str): The pronounced number
    """
    num = number
    # deal with infinity
    if num == float("inf"):
        return "بی نهایت"
    elif num == float("-inf"):
        return "منفی بی نهایت"
    if scientific:
        number = '%E' % num
        n, power = number.replace("+", "").split("E")
        power = int(power)
        if power != 0:
            if ordinals:
                # This handles negatives of powers separately from the normal
                # handling since each call disables the scientific flag
                return '{}{} ضرب در ده به توان {}{}'.format(
                    'منفی ' if float(n) < 0 else '',
                    pronounce_number_fa(
                        abs(float(n)), places, short_scale, False, ordinals=False),
                    'منفی ' if power < 0 else '',
                    pronounce_number_fa(abs(power), places, short_scale, False, ordinals=True))
            else:
                # This handles negatives of powers separately from the normal
                # handling since each call disables the scientific flag
                return '{}{} ضرب در ده به توان {}{}'.format(
                    'منفی ' if float(n) < 0 else '',
                    pronounce_number_fa(
                        abs(float(n)), places, short_scale, False),
                    'منفی ' if power < 0 else '',
                    pronounce_number_fa(abs(power), places, short_scale, False))

    number_names = _NUM_STRING_FA.copy()
    number_names.update(_SCALE_FA)

    digits = [number_names[n] for n in range(0, 20)]

    tens = [number_names[n] for n in range(10, 100, 10)]
    
    hunds = [number_names[n] for n in range(100, 1000, 100)]

    hundreds = [_SCALE_FA[n] for n in _SCALE_FA.keys()]
    hundreds = ['صد'] + hundreds
    # deal with negatives
    result = ""
    if num < 0:
        result = "منفی "
    num = abs(num)

    # check for a direct match
    if num in number_names and not ordinals:
        if num > 1000:
            result += "یک "
        result += number_names[num]
    else:
        def _sub_thousand(n, ordinals=False):
            assert 0 <= n <= 999
            if n in _ORDINAL_FA and ordinals:
                return _ORDINAL_FA[n]
            if n <= 19:
                return digits[n]
            elif n <= 99:
                q, r = divmod(n, 10)
                return tens[q - 1] + (" و " + _sub_thousand(r, ordinals) if r
                                      else "")
            else:
                q, r = divmod(n, 100)
                return hunds[q-1] + (" و " + _sub_thousand(r, ordinals) if r else "")

        def _short_scale(n):
            if n >= max(_SCALE_FA.keys()):
                return "بی نهایت"
            ordi = ordinals

            if int(n) != n:
                ordi = False
            n = int(n)
            assert 0 <= n
            res = []
            for i, z in enumerate(_split_by(n, 1000)):
                if not z:
                    continue
                number = _sub_thousand(z, not i and ordi)

                if i:
                    if i >= len(hundreds):
                        return ""
                    number += " "
                    if ordi:

                        if i * 1000 in _ORDINAL_FA:
                            if z == 1:
                                number = _ORDINAL_FA[i * 1000]
                            else:
                                number += _ORDINAL_FA[i * 1000]
                        else:
                            if n not in _SCALE_FA:
                                num = int("1" + "0" * (len(str(n)) - 2))

                                number += _SCALE_FA[num] + "م"
                            else:
                                number = _SCALE_FA[n] + "م"
                    else:
                        number += hundreds[i]
                if number.startswith("یک هزار"):
                    number = number[3:]
                res.append(number)
                ordi = False

            return " و ".join(reversed(res))

        def _split_by(n, split=1000):
            assert 0 <= n
            res = []
            while n:
                n, r = divmod(n, split)
                res.append(r)
            return res

        result += _short_scale(num)

    # deal with scientific notation unpronounceable as number
    if not result and "e" in str(num):
        return pronounce_number_fa(num, places, short_scale, scientific=True)
    # Deal with fractional part
    elif not num == int(num) and places > 0:
        if result and not result == "منفی ":
            result += " و"
        _num_str = str(num)
        _num_str = _num_str.split(".")[1][0:places]
        print(_num_str)
        result += (" " if result and not result == "منفی " else "") + pronounce_number_fa(int(_num_str))
        if len(_num_str) < 9:
            result += " " + _DECIMAL_STRING_FA[len(_num_str)]
    return result


def nice_time_fa(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
    For example, generate 'پنج و نیم' for speech or '5:30' for
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
            string = dt.strftime("%I:%M")
            if dt.strftime("%p") == "AM":
                string += " قبل از ظهر"
            else:
                string += " بعد از ظهر"
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
        if dt.hour == 0:
            speak = pronounce_number_fa(dt.minute) + " دقیقه‌ی بامداد"
        else:
            speak = pronounce_number_fa(dt.hour)
            if string[3:5] != "00":
                speak += " و "
                speak += pronounce_number_fa(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "دوازده شب"
        
        if dt.hour == 12 and dt.minute == 0:
            return "دوازده ظهر"


        hour = dt.hour % 12 or 12  # 12 hour clock and 0 is spoken as 12
        if dt.minute == 0:
            speak = pronounce_number_fa(hour)
        elif dt.minute == 15:
            speak = pronounce_number_fa(hour) + " و ربع"
        elif dt.minute == 30:
            speak = pronounce_number_fa(hour) + " و نیم"
        elif dt.minute == 45:
            next_hour = (dt.hour + 1) % 12 or 12
            speak = "یک ربع به " + pronounce_number_fa(next_hour)
        elif dt.minute < 30:
            speak = pronounce_number_fa(hour) + " و " + pronounce_number_fa(dt.minute) + " دقیقه"
        else:
            pronounce_number_fa(dt.minute) + "دقیقه به " + pronounce_number_fa(hour)

        if use_ampm:
            if dt.hour > 11:
                speak += " بعد از ظهر"
            else:
                speak += " قبل از ظهر"

        return speak

def nice_duration_fa(duration, speech=True):
    """ Convert duration in seconds to a nice spoken timespan

    Examples:
       duration = 60  ->  "1:00" or "یک دقیقه"
       duration = 163  ->  "2:43" or "یک دقیقه و چهل و سه ثانیه"

    Args:
        duration: time, in seconds
        speech (bool): format for speech (True) or display (False)

    Returns:
        str: timespan as a string
    """

    if isinstance(duration, datetime.timedelta):
        duration = duration.total_seconds()

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
            out += pronounce_number_fa(days) + " "
            out += "روز"
        if hours > 0:
            if out:
                out += " و "
            out += pronounce_number_fa(hours) + " "
            out += "ساعت"
        if minutes > 0:
            if out:
                out += " و "
            out += pronounce_number_fa(minutes) + " "
            out += "دقیقه"
        if seconds > 0:
            if out:
                out += " و "
            out += pronounce_number_fa(seconds) + " "
            out += "ثانیه"
    else:
        # M:SS, MM:SS, H:MM:SS, Dd H:MM:SS format
        out = ""
        if days > 0:
            out = str(days) + " "
        if hours > 0 or days > 0:
            out += str(hours) + ":"
        if minutes < 10 and (hours > 0 or days > 0):
            out += "0"
        out += str(minutes) + ":"
        if seconds < 10:
            out += "0"
        out += str(seconds)

    return out