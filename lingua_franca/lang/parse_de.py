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
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lingua_franca.lang.parse_common import is_numeric, look_for_fractions, \
    extract_numbers_generic, Normalizer
from lingua_franca.lang.common_data_de import _DE_NUMBERS
from lingua_franca.lang.format_de import pronounce_number_de

# TODO: short_scale and ordinals don't do anything here.
# The parameters are present in the function signature for API compatibility
# reasons.


def extract_duration_de(text):
    """
    Convert an german phrase into a number of seconds
    Convert things like:
        "10 Minuten"
        "3 Tage 8 Stunden 10 Minuten und 49 Sekunden"
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
    if not text:
        return None

    text = text.lower()
    # die time_unit values werden für timedelta() mit dem jeweiligen Wert überschrieben
    time_units = {
        'microseconds': 'mikrosekunden',
        'milliseconds': 'millisekunden',
        'seconds': 'sekunden',
        'minutes': 'minuten',
        'hours': 'stunden',
        'days': 'tage',
        'weeks': 'wochen'
    }

    # Einzahl und Mehrzahl
    pattern = r"(?P<value>\d+(?:\.?\d+)?)(?:\s+|\-){unit}[ne]?"

    # TODO Einstiegspunkt für Text-zu-Zahlen Konversion
    #text = _convert_words_to_numbers_de(text)

    for (unit_en, unit_de) in time_units.items():
        unit_pattern = pattern.format(
            unit=unit_de[:-1])  # remove 'n'/'e' from unit
        time_units[unit_en] = 0

        def repl(match):
            time_units[unit_en] += float(match.group(1))
            return ''
        text = re.sub(unit_pattern, repl, text)

    text = text.strip()
    duration = timedelta(**time_units) if any(time_units.values()) else None

    return (duration, text)


def extract_number_de(text, short_scale=True, ordinals=False):
    """
    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.
    Args:
        text (str): the string to normalize
    Returns:
        (int) or (float): The value of extracted number


    undefined articles cannot be suppressed in German:
    'ein Pferd' means 'one horse' and 'a horse'

    """
    # TODO: short_scale and ordinals don't do anything here.
    # The parameters are present in the function signature for API compatibility
    # reasons.
    text = text.lower()
    aWords = text.split()
    aWords = [word for word in aWords if
              word not in ["der", "die", "das", "des", "den", "dem"]]
    and_pass = False
    valPreAnd = False
    val = False
    count = 0
    while count < len(aWords):
        word = aWords[count]
        if is_numeric(word):
            # if word.isdigit():            # doesn't work with decimals
            val = float(word)
        elif is_fractional_de(word):
            val = is_fractional_de(word)
        elif is_ordinal_de(word):
            val = is_ordinal_de(word)
        else:
            if word in _DE_NUMBERS:
                val = _DE_NUMBERS[word]
                if count < (len(aWords) - 1):
                    wordNext = aWords[count + 1]
                else:
                    wordNext = ""
                valNext = is_fractional_de(wordNext)

                if valNext:
                    val = val * valNext
                    aWords[count + 1] = ""

        if not val:
            # look for fractions like "2/3"
            aPieces = word.split('/')
            # if (len(aPieces) == 2 and is_numeric(aPieces[0])
            #   and is_numeric(aPieces[1])):
            if look_for_fractions(aPieces):
                val = float(aPieces[0]) / float(aPieces[1])
            elif and_pass:
                # added to value, quit here
                val = valPreAnd
                break
            else:
                count += 1
                continue

        aWords[count] = ""

        if and_pass:
            aWords[count - 1] = ''  # remove "and"
            val += valPreAnd
        elif count + 1 < len(aWords) and aWords[count + 1] == 'und':
            and_pass = True
            valPreAnd = val
            val = False
            count += 2
            continue
        elif count + 2 < len(aWords) and aWords[count + 2] == 'und':
            and_pass = True
            valPreAnd = val
            val = False
            count += 3
            continue

        break

    return val or False


def extract_datetime_de(text, anchorDate=None, default_time=None):
    def clean_string(s):
        """
            cleans the input string of unneeded punctuation
            and capitalization among other things.

            'am' is a preposition, so cannot currently be used
            for 12 hour date format
        """

        s = s.lower().replace('?', '').replace('.', '').replace(',', '') \
            .replace(' der ', ' ').replace(' den ', ' ').replace(' an ',
                                                                 ' ').replace(
            ' am ', ' ') \
            .replace(' auf ', ' ').replace(' um ', ' ')
        wordList = s.split()

        for idx, word in enumerate(wordList):
            if is_ordinal_de(word) is not False:
                word = str(is_ordinal_de(word))
                wordList[idx] = word

        return wordList

    def date_found():
        return found or \
            (
                datestr != "" or timeStr != "" or
                yearOffset != 0 or monthOffset != 0 or
                dayOffset is True or hrOffset != 0 or
                hrAbs or minOffset != 0 or
                minAbs or secOffset != 0
            )

    if text == "" or not anchorDate:
        return None

    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    dateNow = anchorDate
    today = dateNow.strftime("%w")
    currentYear = dateNow.strftime("%Y")
    fromFlag = False
    datestr = ""
    hasYear = False
    timeQualifier = ""

    timeQualifiersList = ['früh', 'morgens', 'vormittag', 'vormittags',
                          'nachmittag', 'nachmittags', 'abend', 'abends',
                          'nachts']
    markers = ['in', 'am', 'gegen', 'bis', 'für']
    days = ['montag', 'dienstag', 'mittwoch',
            'donnerstag', 'freitag', 'samstag', 'sonntag']
    months = ['januar', 'februar', 'märz', 'april', 'mai', 'juni',
              'juli', 'august', 'september', 'october', 'november',
              'dezember']
    monthsShort = ['jan', 'feb', 'mär', 'apr', 'mai', 'juni', 'juli', 'aug',
                   'sept', 'oct', 'nov', 'dez']

    validFollowups = days + months + monthsShort
    validFollowups.append("heute")
    validFollowups.append("morgen")
    validFollowups.append("nächste")
    validFollowups.append("nächster")
    validFollowups.append("nächstes")
    validFollowups.append("nächsten")
    validFollowups.append("nächstem")
    validFollowups.append("letzte")
    validFollowups.append("letzter")
    validFollowups.append("letztes")
    validFollowups.append("letzten")
    validFollowups.append("letztem")
    validFollowups.append("jetzt")

    words = clean_string(text)

    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""

        # this isn't in clean string because I don't want to save back to words

        if word != 'morgen' and word != 'übermorgen':
            if word[-2:] == "en":
                word = word[:-2]  # remove en
        if word != 'heute':
            if word[-1:] == "e":
                word = word[:-1]  # remove plural for most nouns

        start = idx
        used = 0
        # save timequalifier for later
        if word in timeQualifiersList:
            timeQualifier = word
            # parse today, tomorrow, day after tomorrow
        elif word == "heute" and not fromFlag:
            dayOffset = 0
            used += 1
        elif word == "morgen" and not fromFlag and wordPrev != "am" and \
                wordPrev not in days:  # morgen means tomorrow if not "am
            # Morgen" and not [day of the week] morgen
            dayOffset = 1
            used += 1
        elif word == "übermorgen" and not fromFlag:
            dayOffset = 2
            used += 1
            # parse 5 days, 10 weeks, last week, next week
        elif word == "tag" or word == "tage":
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev)
                start -= 1
                used = 2
        elif word == "woch" and not fromFlag:
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev) * 7
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                dayOffset = 7
                start -= 1
                used = 2
            elif wordPrev[:5] == "letzt":
                dayOffset = -7
                start -= 1
                used = 2
                # parse 10 months, next month, last month
        elif word == "monat" and not fromFlag:
            if wordPrev[0].isdigit():
                monthOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                monthOffset = 1
                start -= 1
                used = 2
            elif wordPrev[:5] == "letzt":
                monthOffset = -1
                start -= 1
                used = 2
                # parse 5 years, next year, last year
        elif word == "jahr" and not fromFlag:
            if wordPrev[0].isdigit():
                yearOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
                yearOffset = 1
                start -= 1
                used = 2
            elif wordPrev[:6] == "nächst":
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
            if wordNext == "morgen":  # morgen means morning if preceded by
                # the day of the week
                words[idx + 1] = "früh"
            if wordPrev[:6] == "nächst":
                dayOffset += 7
                used += 1
                start -= 1
            elif wordPrev[:5] == "letzt":
                dayOffset -= 7
                used += 1
                start -= 1

        # parse 15 Mai, Mai der 20ste, Dez 18
        elif word in months or word in monthsShort and not fromFlag:
            try:
                m = months.index(word)
            except ValueError:
                m = monthsShort.index(word)
            used += 1
            datestr = months[m]
            #commonly spoken : 15(.=gets replaced) Mai <Year>/<time>
            if wordPrev and (wordPrev[0].isdigit() or
                             (((wordNext == "der") or (wordNext == "den")) and
                             wordNextNext[0].isdigit())):
                #Mai der fünfte(5)
                if ((wordNext == "der") or (wordNext == "den")) and wordNextNext[0].isdigit():
                    datestr += " " + words[idx + 2]
                    used += 1
                    start -= 1
                else:
                    datestr += " " + wordPrev
                start -= 1
                used += 1
                if wordNext and wordNext[0].isdigit():
                    #normally the time comes in as ##:## and therefor
                    #would break int(wordnext)
                    if ':' in wordNext:
                        tmp_word = wordNext.split(':')
                        wordNext = tmp_word[0]
                    #determine if wordnext is year data; eg 3 Januar 10:10 uhr
                    #10:10 / 10 would be seen as such, leaving us with no time data
                    if int(wordNext) > 60:
                        datestr += " " + wordNext
                        used += 1
                        hasYear = True
                    else:
                        hasYear = False
            # Mai <Year>
            elif wordNext and wordNext[0].isdigit():
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July
        if (
                word == "von" or word == "nach" or word == "ab") and wordNext \
                in validFollowups:
            used = 2
            fromFlag = True
            if wordNext == "morgen" and wordPrev != "am" and \
                    wordPrev not in days:  # morgen means tomorrow if not "am
                #  Morgen" and not [day of the week] morgen:
                dayOffset += 1
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
                if wordNext[:6] == "nächst":
                    tmpOffset += 7
                    used += 1
                    start -= 1
                elif wordNext[:5] == "letzt":
                    tmpOffset -= 7
                    used += 1
                    start -= 1
                dayOffset += tmpOffset
        if used > 0:
            if start - 1 > 0 and words[start - 1].startswith("diese"):
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in markers:
                words[start - 1] = ""
            found = True
            daySpecified = True

    # parse time
    timeStr = ""
    hrOffset = 0
    minOffset = 0
    secOffset = 0
    hrAbs = None
    minAbs = None

    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""
        wordNextNextNextNext = words[idx + 4] if idx + 4 < len(words) else ""

        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word[:6] == "mittag":
            hrAbs = 12
            used += 1
        elif word[:11] == "mitternacht":
            hrAbs = 0
            used += 1
        elif word == "morgens" or (
                wordPrev == "am" and word == "morgen") or word == "früh":
            if not hrAbs:
                hrAbs = 8
            used += 1
        elif word[:10] == "nachmittag":
            if not hrAbs:
                hrAbs = 15
            used += 1
        elif word[:5] == "abend":
            if not hrAbs:
                hrAbs = 19
            used += 1
            # parse half an hour, quarter hour
        elif word == "stunde" and \
                (wordPrev in markers or wordPrevPrev in markers):
            if wordPrev[:4] == "halb":
                minOffset = 30
            elif wordPrev == "viertel":
                minOffset = 15
            elif wordPrev == "dreiviertel":
                minOffset = 45
            else:
                hrOffset = 1
            if wordPrevPrev in markers:
                words[idx - 2] = ""
            words[idx - 1] = ""
            used += 1
            hrAbs = -1
            minAbs = -1
            # parse 5:00 am, 12:00 p.m., etc
        elif word[0].isdigit():
            isTime = True
            strHH = ""
            strMM = ""
            remainder = ""
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
                    elif nextWord == "abends":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "am" and wordNextNext == "morgen":
                        remainder = "am"
                        used += 2
                    elif wordNext == "am" and wordNextNext == "nachmittag":
                        remainder = "pm"
                        used += 2
                    elif wordNext == "am" and wordNextNext == "abend":
                        remainder = "pm"
                        used += 2
                    elif wordNext == "morgens":
                        remainder = "am"
                        used += 1
                    elif wordNext == "nachmittags":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "abends":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "heute" and wordNextNext == "morgen":
                        remainder = "am"
                        used = 2
                    elif wordNext == "heute" and wordNextNext == "nachmittag":
                        remainder = "pm"
                        used = 2
                    elif wordNext == "heute" and wordNextNext == "abend":
                        remainder = "pm"
                        used = 2
                    elif wordNext == "nachts":
                        if strHH > 4:
                            remainder = "pm"
                        else:
                            remainder = "am"
                        used += 1
                    else:
                        if timeQualifier != "":
                            if strHH <= 12 and \
                                    (timeQualifier == "abends" or
                                     timeQualifier == "nachmittags"):
                                strHH += 12  # what happens when strHH is 24?
            else:
                # try to parse # s without colons
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
                else:
                    if wordNext == "stund" and int(word) < 100:
                        # "in 3 hours"
                        hrOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext == "minut":
                        # "in 10 minutes"
                        minOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext == "sekund":
                        # in 5 seconds
                        secOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1

                    elif wordNext == "uhr":
                        strHH = word
                        used += 1
                        isTime = True
                        if wordNextNext == timeQualifier:
                            strMM = ""
                            if wordNextNext[:10] == "nachmittag":
                                used += 1
                                remainder = "pm"
                            elif wordNextNext == "am" and wordNextNextNext == \
                                    "nachmittag":
                                used += 2
                                remainder = "pm"
                            elif wordNextNext[:5] == "abend":
                                used += 1
                                remainder = "pm"
                            elif wordNextNext == "am" and wordNextNextNext == \
                                    "abend":
                                used += 2
                                remainder = "pm"
                            elif wordNextNext[:7] == "morgens":
                                used += 1
                                remainder = "am"
                            elif wordNextNext == "am" and wordNextNextNext == \
                                    "morgen":
                                used += 2
                                remainder = "am"
                            elif wordNextNext == "nachts":
                                used += 1
                                if 8 <= int(word) <= 12:
                                    remainder = "pm"
                                else:
                                    remainder = "am"

                        elif is_numeric(wordNextNext):
                            strMM = wordNextNext
                            used += 1
                            if wordNextNextNext == timeQualifier:
                                if wordNextNextNext[:10] == "nachmittag":
                                    used += 1
                                    remainder = "pm"
                                elif wordNextNextNext == "am" and \
                                        wordNextNextNextNext == "nachmittag":
                                    used += 2
                                    remainder = "pm"
                                elif wordNextNextNext[:5] == "abend":
                                    used += 1
                                    remainder = "pm"
                                elif wordNextNextNext == "am" and \
                                        wordNextNextNextNext == "abend":
                                    used += 2
                                    remainder = "pm"
                                elif wordNextNextNext[:7] == "morgens":
                                    used += 1
                                    remainder = "am"
                                elif wordNextNextNext == "am" and \
                                        wordNextNextNextNext == "morgen":
                                    used += 2
                                    remainder = "am"
                                elif wordNextNextNext == "nachts":
                                    used += 1
                                    if 8 <= int(word) <= 12:
                                        remainder = "pm"
                                    else:
                                        remainder = "am"

                    elif wordNext == timeQualifier:
                        strHH = word
                        strMM = 00
                        isTime = True
                        if wordNext[:10] == "nachmittag":
                            used += 1
                            remainder = "pm"
                        elif wordNext == "am" and wordNextNext == "nachmittag":
                            used += 2
                            remainder = "pm"
                        elif wordNext[:5] == "abend":
                            used += 1
                            remainder = "pm"
                        elif wordNext == "am" and wordNextNext == "abend":
                            used += 2
                            remainder = "pm"
                        elif wordNext[:7] == "morgens":
                            used += 1
                            remainder = "am"
                        elif wordNext == "am" and wordNextNext == "morgen":
                            used += 2
                            remainder = "am"
                        elif wordNext == "nachts":
                            used += 1
                            if 8 <= int(word) <= 12:
                                remainder = "pm"
                            else:
                                remainder = "am"

                # if timeQualifier != "":
                #     military = True
                # else:
                #     isTime = False

            strHH = int(strHH) if strHH else 0
            strMM = int(strMM) if strMM else 0
            strHH = strHH + 12 if remainder == "pm" and strHH < 12 else strHH
            strHH = strHH - 12 if remainder == "am" and strHH >= 12 else strHH
            if strHH > 24 or strMM > 59:
                isTime = False
                used = 0
            if isTime:
                hrAbs = strHH * 1
                minAbs = strMM * 1
                used += 1
        if used > 0:
            # removed parsed words from the sentence
            for i in range(used):
                words[idx + i] = ""

            if wordPrev == "Uhr":
                words[words.index(wordPrev)] = ""

            if wordPrev == "früh":
                hrOffset = -1
                words[idx - 1] = ""
                idx -= 1
            elif wordPrev == "spät":
                hrOffset = 1
                words[idx - 1] = ""
                idx -= 1
            if idx > 0 and wordPrev in markers:
                words[idx - 1] = ""
            if idx > 1 and wordPrevPrev in markers:
                words[idx - 2] = ""

            idx += used - 1
            found = True

    # check that we found a date
    if not date_found():
        return None

    if dayOffset is False:
        dayOffset = 0

    # perform date manipulation

    extractedDate = dateNow
    extractedDate = extractedDate.replace(microsecond=0,
                                          second=0,
                                          minute=0,
                                          hour=0)
    if datestr != "":
        en_months = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november',
                     'december']
        en_monthsShort = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july',
                          'aug',
                          'sept', 'oct', 'nov', 'dec']
        for idx, en_month in enumerate(en_months):
            datestr = datestr.replace(months[idx], en_month)
        for idx, en_month in enumerate(en_monthsShort):
            datestr = datestr.replace(monthsShort[idx], en_month)

        temp = datetime.strptime(datestr, "%B %d").replace(tzinfo=extractedDate.tzinfo)
        if not hasYear:
            temp = temp.replace(year=extractedDate.year)
            if extractedDate < temp:
                extractedDate = extractedDate.replace(year=int(currentYear),
                                                      month=int(
                                                          temp.strftime(
                                                              "%m")),
                                                      day=int(temp.strftime(
                                                          "%d")))
            else:
                extractedDate = extractedDate.replace(
                    year=int(currentYear) + 1,
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")))
        else:
            extractedDate = extractedDate.replace(
                year=int(temp.strftime("%Y")),
                month=int(temp.strftime("%m")),
                day=int(temp.strftime("%d")))

    if timeStr != "":
        temp = datetime(timeStr)
        extractedDate = extractedDate.replace(hour=temp.strftime("%H"),
                                              minute=temp.strftime("%M"),
                                              second=temp.strftime("%S"))

    if yearOffset != 0:
        extractedDate = extractedDate + relativedelta(years=yearOffset)
    if monthOffset != 0:
        extractedDate = extractedDate + relativedelta(months=monthOffset)
    if dayOffset != 0:
        extractedDate = extractedDate + relativedelta(days=dayOffset)

    if hrAbs is None and minAbs is None and default_time:
        hrAbs = default_time.hour
        minAbs = default_time.minute

    if hrAbs != -1 and minAbs != -1:

        extractedDate = extractedDate + relativedelta(hours=hrAbs or 0,
                                                      minutes=minAbs or 0)
        if (hrAbs or minAbs) and datestr == "":
            if not daySpecified and dateNow > extractedDate:
                extractedDate = extractedDate + relativedelta(days=1)
    if hrOffset != 0:
        extractedDate = extractedDate + relativedelta(hours=hrOffset)
    if minOffset != 0:
        extractedDate = extractedDate + relativedelta(minutes=minOffset)
    if secOffset != 0:
        extractedDate = extractedDate + relativedelta(seconds=secOffset)
    for idx, word in enumerate(words):
        if words[idx] == "und" and words[idx - 1] == "" \
                and words[idx + 1] == "":
            words[idx] = ""

    resultStr = " ".join(words)
    resultStr = ' '.join(resultStr.split())

    return [extractedDate, resultStr]


def is_fractional_de(input_str, short_scale=True):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        input_str (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    if input_str.lower().startswith("halb"):
        return 0.5

    if input_str.lower() == "drittel":
        return 1.0 / 3
    elif input_str.endswith('tel'):
        if input_str.endswith('stel'):
            input_str = input_str[:len(input_str) - 4]  # e.g. "hundertstel"
        else:
            input_str = input_str[:len(input_str) - 3]  # e.g. "fünftel"
        if input_str.lower() in _DE_NUMBERS:
            return 1.0 / (_DE_NUMBERS[input_str.lower()])

    return False


def is_ordinal_de(input_str):
    """
    This function takes the given text and checks if it is an ordinal number.

    Args:
        input_str (str): the string to check if ordinal
    Returns:
        (bool) or (float): False if not an ordinal, otherwise the number
        corresponding to the ordinal

    ordinals for 1, 3, 7 and 8 are irregular

    only works for ordinals corresponding to the numbers in _DE_NUMBERS

    """

    lowerstr = input_str.lower()

    if lowerstr.startswith("erste"):
        return 1
    if lowerstr.startswith("dritte"):
        return 3
    if lowerstr.startswith("siebte"):
        return 7
    if lowerstr.startswith("achte"):
        return 8

    if lowerstr[-3:] == "ste":  # from 20 suffix is -ste*
        lowerstr = lowerstr[:-3]
        if lowerstr in _DE_NUMBERS:
            return _DE_NUMBERS[lowerstr]

    if lowerstr[-4:] in ["ster", "stes", "sten", "stem"]:
        lowerstr = lowerstr[:-4]
        if lowerstr in _DE_NUMBERS:
            return _DE_NUMBERS[lowerstr]

    if lowerstr[-2:] == "te":  # below 20 suffix is -te*
        lowerstr = lowerstr[:-2]
        if lowerstr in _DE_NUMBERS:
            return _DE_NUMBERS[lowerstr]

    if lowerstr[-3:] in ["ter", "tes", "ten", "tem"]:
        lowerstr = lowerstr[:-3]
        if lowerstr in _DE_NUMBERS:
            return _DE_NUMBERS[lowerstr]

    return False


def normalize_de(text, remove_articles=True):
    """ German string normalization """
    # TODO return GermanNormalizer().normalize(text, remove_articles)
    words = text.split()  # this also removed extra spaces
    normalized = ""
    for word in words:
        if remove_articles and word in ["der", "die", "das", "des", "den",
                                        "dem"]:
            continue

        # Expand common contractions, e.g. "isn't" -> "is not"
        contraction = ["net", "nett"]
        if word in contraction:
            expansion = ["nicht", "nicht"]
            word = expansion[contraction.index(word)]

        # Convert numbers into digits, e.g. "two" -> "2"

        if word in _DE_NUMBERS:
            word = str(_DE_NUMBERS[word])

        normalized += " " + word

    return normalized[1:]  # strip the initial space


def extract_numbers_de(text, short_scale=True, ordinals=False):
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
    return extract_numbers_generic(text, pronounce_number_de, extract_number_de,
                                   short_scale=short_scale, ordinals=ordinals)


class GermanNormalizer(Normalizer):
    """ TODO implement language specific normalizer"""
