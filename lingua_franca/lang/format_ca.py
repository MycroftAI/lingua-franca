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
from lingua_franca.lang.common_data_ca import _FRACTION_STRING_CA, \
    _NUM_STRING_CA


def nice_number_ca(number, speech, denominators=range(1, 21)):
    """ Catalan helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "4 i mig" for speech and "4 1/2" for text

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
    # denominador
    den_str = _FRACTION_STRING_CA[den]
    # fraccions
    if whole == 0:
        if num == 1:
            # un desè
            return_string = 'un {}'.format(den_str)
        else:
            # tres mig
            return_string = '{} {}'.format(num, den_str)
    # inteiros >10
    elif num == 1:
        # trenta-un
        return_string = '{}-{}'.format(whole, den_str)
    # inteiros >10 com fracções
    else:
        # vint i 3 desens
        return_string = '{} i {} {}'.format(whole, num, den_str)
    # plural
    if num > 1:
        return_string += 's'
    return return_string


def pronounce_number_ca(number, places=2):
    """
    Convert a number to it's spoken equivalent
     For example, '5.2' would return 'cinc coma dos'
     Args:
        number(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
    Returns:
        (str): The pronounced number
    """
    if abs(number) >= 100:
        # TODO: Support n > 100
        return str(number)

    result = ""
    if number < 0:
        result = "menys "
    number = abs(number)

    if number >= 20:
        tens = int(number - int(number) % 10)
        ones = int(number - tens)
        result += _NUM_STRING_CA[tens]
        if ones > 0:
            if tens == 20:
                result += "-i-" + _NUM_STRING_CA[ones]
            else:
                result += "-" + _NUM_STRING_CA[ones]
    else:
        result += _NUM_STRING_CA[int(number)]

    # Deal with decimal part, in Catalan is commonly used the comma
    # instead the dot. Decimal part can be written both with comma
    # and dot, but when pronounced, its pronounced "coma"
    if not number == int(number) and places > 0:
        if abs(number) < 1.0 and (result == "menys " or not result):
            result += "zero"
        result += " coma"
        _num_str = str(number)
        _num_str = _num_str.split(".")[1][0:places]
        for char in _num_str:
            result += " " + _NUM_STRING_CA[int(char)]
    return result


def nice_time_ca(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format
     For example, generate 'cinc trenta' for speech or '5:30' for
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
    speak = ""
    if use_24hour:
        # simply speak the number
        if dt.hour == 1:
            speak += "una"
        elif dt.hour == 2:
            speak += "dues"
        elif dt.hour == 21:
            speak += "vit-i-una"
        elif dt.hour == 22:
            speak += "vit-i-dues"
        else:
            speak += pronounce_number_ca(dt.hour)

        if dt.minute > 0:
            speak += " i " + pronounce_number_ca(dt.minute)

    else:
        # speak number and add daytime identifier
        # (equivalent to "in the morning")
        if dt.hour == 0 and dt.minute == 0:
            speak += "mitjanit"
        elif dt.hour == 12 and dt.minute == 0:
            speak += "migdia"
        else:
            if dt.hour == 0:
                speak += "dotze"
            # 1 and 2 are pronounced in female form when talking about hours
            elif dt.hour == 1 or dt.hour == 13:
                speak += "una"
            elif dt.hour == 2 or dt.hour == 14:
                speak += "dues"
            elif dt.hour < 13:
                speak = pronounce_number_ca(dt.hour)
            else:
                speak = pronounce_number_ca(dt.hour - 12)

            if dt.minute != 0:
                speak += " i " + pronounce_number_ca(dt.minute)
            # exact time
            if dt.minute == 0 and not use_ampm:
                # 3:00
                speak += " en punt"
            #TODO: review day-periods
            if use_ampm:
                if dt.hour == 0:
                    speak += " de la nit"
                elif dt.hour >= 1 and dt.hour < 6:
                    speak += " de la matinada"
                elif dt.hour >= 6 and dt.hour < 12:
                    speak += " del matí"
                elif dt.hour == 12:
                    speak += " del migdia"
                elif dt.hour >= 13 and dt.hour <= 18:
                    speak += " de la tarda"
                elif dt.hour >= 19 and dt.hour < 21:
                    speak += " del vespre"
                elif dt.hour != 0 and dt.hour != 12:
                    speak += " de la nit"
    return speak
