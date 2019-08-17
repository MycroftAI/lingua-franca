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

from datetime import datetime
from dateutil.relativedelta import relativedelta

from lingua_franca.lang.parse_common import is_numeric, look_for_fractions, \
    invert_dict, ReplaceableNumber, partition_list, tokenize, Token

from lingua_franca.lang.common_data_pt import _PT_ARTICLES, _NUM_STRING_PT, \
    _LONG_ORDINAL_PT, _LONG_SCALE_PT, _SHORT_SCALE_PT, _SHORT_ORDINAL_PT, \
    _FRACTION_MARKER_PT, _DECIMAL_MARKER_PT, _PT_NUMBERS, _SUFFIX_FRACTION_MARKER_PT, \
    _NEGATIVES_PT, _NEGATIVE_SUFFIX_MARKER_PT, _SUM_MARKER_PT


def generate_plurals_pt(originals):
    """
    Return a new set or dict containing the plural form of the original values,

    In Portuguese this means all with 's' appended to them.

    Args:
        originals set(str) or dict(str, any): values to pluralize

    Returns:
        set(str) or dict(str, any)

    """
    if isinstance(originals, dict):
        return {key + 's': value for key, value in originals.items()}
    return {value + "s" for value in originals}


_MULTIPLIES_LONG_SCALE_PT = set(_LONG_SCALE_PT.values()) | \
                            generate_plurals_pt(_LONG_SCALE_PT.values())

_MULTIPLIES_SHORT_SCALE_PT = set(_SHORT_SCALE_PT.values()) | \
                             generate_plurals_pt(_SHORT_SCALE_PT.values())

_STRING_NUM_PT = invert_dict(_NUM_STRING_PT)
_STRING_NUM_PT.update(generate_plurals_pt(_STRING_NUM_PT))
_STRING_NUM_PT.update({
    "meio": 0.5,
    "meios": 0.5,
    "par": 2
})
_STRING_NUM_PT.update(_PT_NUMBERS)

_STRING_SHORT_ORDINAL_PT = invert_dict(_SHORT_ORDINAL_PT)
_STRING_LONG_ORDINAL_PT = invert_dict(_LONG_ORDINAL_PT)


def isFractional_pt(input_str, short_scale=False):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        text (str): the string to check if fractional
        short_scale (bool): use short scale if True, long scale if False
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    if input_str.endswith('s', -1):
        input_str = input_str[:len(input_str) - 1]  # e.g. "fifths"

    aFrac = ["meio", u"terço", "quarto", "quinto", "sexto",
             "setimo", "oitavo", "nono", u"décimo"]

    if input_str.lower() in aFrac:
        return 1.0 / (aFrac.index(input_str) + 2)
    if input_str == u"vigésimo":
        return 1.0 / 20
    if input_str == u"trigésimo":
        return 1.0 / 30
    if input_str == u"centésimo":
        return 1.0 / 100
    if input_str == u"milésimo":
        return 1.0 / 1000
    if (input_str == u"sétimo" or input_str == "septimo" or
            input_str == u"séptimo"):
        return 1.0 / 7

    return False


def _pt_number_parse_helper(words, i):
    def pt_cte(i, s):
        if i < len(words) and s == words[i]:
            return s, i + 1
        return None

    def pt_number_word(i, mi, ma):
        if i < len(words):
            v = _STRING_NUM_PT.get(words[i])
            if v and v >= mi and v <= ma:
                return v, i + 1
        return None

    def pt_number_1_99(i):
        r1 = pt_number_word(i, 1, 29)
        if r1:
            return r1

        r1 = pt_number_word(i, 30, 90)
        if r1:
            v1, i1 = r1
            r2 = pt_cte(i1, "e")
            if r2:
                i2 = r2[1]
                r3 = pt_number_word(i2, 1, 9)
                if r3:
                    v3, i3 = r3
                    return v1 + v3, i3
            return r1
        return None

    def pt_number_1_999(i):
        # [2-9]cientos [1-99]?
        r1 = pt_number_word(i, 100, 900)
        if r1:
            v1, i1 = r1
            r2 = pt_number_1_99(i1)
            if r2:
                v2, i2 = r2
                return v1 + v2, i2
            else:
                return r1

        # [1-99]
        r1 = pt_number_1_99(i)
        if r1:
            return r1

        return None

    def pt_number(i):
        # check for cero
        r1 = pt_number_word(i, 0, 0)
        if r1:
            return r1

        # check for [1-999] (mil [0-999])?
        r1 = pt_number_1_999(i)
        if r1:
            v1, i1 = r1
            r2 = pt_cte(i1, "mil")
            if r2:
                i2 = r2[1]
                r3 = pt_number_1_999(i2)
                if r3:
                    v3, i3 = r3
                    return v1 * 1000 + v3, i3
                else:
                    return v1 * 1000, i2
            else:
                return r1
        return None

    return pt_number(i)


def normalize_pt(text, remove_pt_articles):
    """ PT string normalization """

    words = text.split()  # this also removed extra spaces
    # Convert numbers into digits, e.g. "dois" -> "2"
    normalized = ""
    i = 0
    while i < len(words):
        word = words[i]
        # remove articles
        if remove_pt_articles and word in _PT_ARTICLES:
            i += 1
            continue

        # Convert numbers into digits
        r = _pt_number_parse_helper(words, i)
        if r:
            v, i = r
            normalized += " " + str(v)
            continue

        # NOTE temporary , handle some numbers above >999
        if word in _PT_NUMBERS:
            word = str(_PT_NUMBERS[word])
        # end temporary

        normalized += " " + word
        i += 1
    # some articles in pt-pt can not be removed, but many words can
    # this is experimental and some meaning may be lost
    # maybe agressive should default to False
    # only usage will tell, as a native speaker this seems reasonable
    return pt_pruning(normalized[1:], agressive=remove_pt_articles)


def extract_datetime_pt(input_str, currentDate, default_time):
    def clean_string(s):
        # cleans the input string of unneeded punctuation and capitalization
        # among other things
        symbols = [".", ",", ";", "?", "!", u"º", u"ª"]
        noise_words = ["o", "os", "a", "as", "do", "da", "dos", "das", "de",
                       "ao", "aos"]

        for word in symbols:
            s = s.replace(word, "")
        for word in noise_words:
            s = s.replace(" " + word + " ", " ")
        s = s.lower().replace(
            u"á",
            "a").replace(
            u"ç",
            "c").replace(
            u"à",
            "a").replace(
            u"ã",
            "a").replace(
            u"é",
            "e").replace(
            u"è",
            "e").replace(
            u"ê",
            "e").replace(
            u"ó",
            "o").replace(
            u"ò",
            "o").replace(
            "-",
            " ").replace(
            "_",
            "")
        # handle synonims and equivalents, "tomorrow early = tomorrow morning
        synonims = {"manha": ["manhazinha", "cedo", "cedinho"],
                    "tarde": ["tardinha", "tarde"],
                    "noite": ["noitinha", "anoitecer"],
                    "todos": ["ao", "aos"],
                    "em": ["do", "da", "dos", "das", "de"]}
        for syn in synonims:
            for word in synonims[syn]:
                s = s.replace(" " + word + " ", " " + syn + " ")
        # relevant plurals, cant just extract all s in pt
        wordlist = ["manhas", "noites", "tardes", "dias", "semanas", "anos",
                    "minutos", "segundos", "nas", "nos", "proximas",
                    "seguintes", "horas"]
        for _, word in enumerate(wordlist):
            s = s.replace(word, word.rstrip('s'))
        s = s.replace("meses", "mes").replace("anteriores", "anterior")
        return s

    def date_found():
        return found or \
               (
                       datestr != "" or timeStr != "" or
                       yearOffset != 0 or monthOffset != 0 or
                       dayOffset is True or hrOffset != 0 or
                       hrAbs or minOffset != 0 or
                       minAbs or secOffset != 0
               )

    if input_str == "" or not currentDate:
        return None

    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    dateNow = currentDate
    today = dateNow.strftime("%w")
    currentYear = dateNow.strftime("%Y")
    fromFlag = False
    datestr = ""
    hasYear = False
    timeQualifier = ""

    words = clean_string(input_str).split(" ")
    timeQualifiersList = ['manha', 'tarde', 'noite']
    time_indicators = ["em", "as", "nas", "pelas", "volta", "depois", "estas",
                       "no", "dia", "hora"]
    days = ['segunda', 'terca', 'quarta',
            'quinta', 'sexta', 'sabado', 'domingo']
    months = ['janeiro', 'febreiro', 'marco', 'abril', 'maio', 'junho',
              'julho', 'agosto', 'setembro', 'outubro', 'novembro',
              'dezembro']
    monthsShort = ['jan', 'feb', 'mar', 'abr', 'mai', 'jun', 'jul', 'ag',
                   'set', 'out', 'nov', 'dec']
    nexts = ["proximo", "proxima"]
    suffix_nexts = ["seguinte", "subsequente", "seguir"]
    lasts = ["ultimo", "ultima"]
    suffix_lasts = ["passada", "passado", "anterior", "antes"]
    nxts = ["depois", "seguir", "seguida", "seguinte", "proxima", "proximo"]
    prevs = ["antes", "ante", "previa", "previamente", "anterior"]
    froms = ["partir", "em", "para", "na", "no", "daqui", "seguir",
             "depois", "por", "proxima", "proximo", "da", "do", "de"]
    thises = ["este", "esta", "deste", "desta", "neste", "nesta", "nesse",
              "nessa"]
    froms += thises
    lists = nxts + prevs + froms + time_indicators
    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""

        start = idx
        used = 0
        # save timequalifier for later
        if word in timeQualifiersList:
            timeQualifier = word

        # parse today, tomorrow, yesterday
        elif word == "hoje" and not fromFlag:
            dayOffset = 0
            used += 1
        elif word == "amanha" and not fromFlag:
            dayOffset = 1
            used += 1
        elif word == "ontem" and not fromFlag:
            dayOffset -= 1
            used += 1
        # "before yesterday" and "before before yesterday"
        elif (word == "anteontem" or
              (word == "ante" and wordNext == "ontem")) and not fromFlag:
            dayOffset -= 2
            used += 1
            if wordNext == "ontem":
                used += 1
        elif word == "ante" and wordNext == "ante" and wordNextNext == \
                "ontem" and not fromFlag:
            dayOffset -= 3
            used += 3
        elif word == "anteanteontem" and not fromFlag:
            dayOffset -= 3
            used += 1
        # day after tomorrow
        elif word == "depois" and wordNext == "amanha" and not fromFlag:
            dayOffset += 2
            used = 2
        # day before yesterday
        elif word == "antes" and wordNext == "ontem" and not fromFlag:
            dayOffset -= 2
            used = 2
        # parse 5 days, 10 weeks, last week, next week, week after
        elif word == "dia":
            if wordNext == "depois" or wordNext == "antes":
                used += 1
                if wordPrev and wordPrev[0].isdigit():
                    dayOffset += int(wordPrev)
                    start -= 1
                    used += 1
            elif (wordPrev and wordPrev[0].isdigit() and
                  wordNext not in months and
                  wordNext not in monthsShort):
                dayOffset += int(wordPrev)
                start -= 1
                used += 2
            elif wordNext and wordNext[0].isdigit() and wordNextNext not in \
                    months and wordNextNext not in monthsShort:
                dayOffset += int(wordNext)
                start -= 1
                used += 2

        elif word == "semana" and not fromFlag:
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev) * 7
                start -= 1
                used = 2
            for w in nexts:
                if wordPrev == w:
                    dayOffset = 7
                    start -= 1
                    used = 2
            for w in lasts:
                if wordPrev == w:
                    dayOffset = -7
                    start -= 1
                    used = 2
            for w in suffix_nexts:
                if wordNext == w:
                    dayOffset = 7
                    start -= 1
                    used = 2
            for w in suffix_lasts:
                if wordNext == w:
                    dayOffset = -7
                    start -= 1
                    used = 2
        # parse 10 months, next month, last month
        elif word == "mes" and not fromFlag:
            if wordPrev[0].isdigit():
                monthOffset = int(wordPrev)
                start -= 1
                used = 2
            for w in nexts:
                if wordPrev == w:
                    monthOffset = 7
                    start -= 1
                    used = 2
            for w in lasts:
                if wordPrev == w:
                    monthOffset = -7
                    start -= 1
                    used = 2
            for w in suffix_nexts:
                if wordNext == w:
                    monthOffset = 7
                    start -= 1
                    used = 2
            for w in suffix_lasts:
                if wordNext == w:
                    monthOffset = -7
                    start -= 1
                    used = 2
        # parse 5 years, next year, last year
        elif word == "ano" and not fromFlag:
            if wordPrev[0].isdigit():
                yearOffset = int(wordPrev)
                start -= 1
                used = 2
            for w in nexts:
                if wordPrev == w:
                    yearOffset = 7
                    start -= 1
                    used = 2
            for w in lasts:
                if wordPrev == w:
                    yearOffset = -7
                    start -= 1
                    used = 2
            for w in suffix_nexts:
                if wordNext == w:
                    yearOffset = 7
                    start -= 1
                    used = 2
            for w in suffix_lasts:
                if wordNext == w:
                    yearOffset = -7
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
            for w in nexts:
                if wordPrev == w:
                    dayOffset += 7
                    used += 1
                    start -= 1
            for w in lasts:
                if wordPrev == w:
                    dayOffset -= 7
                    used += 1
                    start -= 1
            for w in suffix_nexts:
                if wordNext == w:
                    dayOffset += 7
                    used += 1
                    start -= 1
            for w in suffix_lasts:
                if wordNext == w:
                    dayOffset -= 7
                    used += 1
                    start -= 1
            if wordNext == "feira":
                used += 1
        # parse 15 of July, June 20th, Feb 18, 19 of February
        elif word in months or word in monthsShort:
            try:
                m = months.index(word)
            except ValueError:
                m = monthsShort.index(word)
            used += 1
            datestr = months[m]
            if wordPrev and wordPrev[0].isdigit():
                # 13 maio
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
                # maio 13
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordPrevPrev and wordPrevPrev[0].isdigit():
                # 13 dia maio
                datestr += " " + wordPrevPrev

                start -= 2
                used += 2
                if wordNext and word[0].isdigit():
                    datestr += " " + wordNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordNextNext and wordNextNext[0].isdigit():
                # maio dia 13
                datestr += " " + wordNextNext
                used += 2
                if wordNextNextNext and wordNextNextNext[0].isdigit():
                    datestr += " " + wordNextNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            if datestr in months:
                datestr = ""

        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July
        validFollowups = days + months + monthsShort
        validFollowups.append("hoje")
        validFollowups.append("amanha")
        validFollowups.append("ontem")
        validFollowups.append("anteontem")
        validFollowups.append("agora")
        validFollowups.append("ja")
        validFollowups.append("ante")

        # TODO debug word "depois" that one is failing for some reason
        if word in froms and wordNext in validFollowups:

            if not (wordNext == "amanha" and wordNext == "ontem") and not (
                    word == "depois" or word == "antes" or word == "em"):
                used = 2
                fromFlag = True
            if wordNext == "amanha" and word != "depois":
                dayOffset += 1
            elif wordNext == "ontem":
                dayOffset -= 1
            elif wordNext == "anteontem":
                dayOffset -= 2
            elif wordNext == "ante" and wordNextNext == "ontem":
                dayOffset -= 2
            elif (wordNext == "ante" and wordNext == "ante" and
                  wordNextNextNext == "ontem"):
                dayOffset -= 3
            elif wordNext in days:
                d = days.index(wordNext)
                tmpOffset = (d + 1) - int(today)
                used = 2
                if wordNextNext == "feira":
                    used += 1
                if tmpOffset < 0:
                    tmpOffset += 7
                if wordNextNext:
                    if wordNextNext in nxts:
                        tmpOffset += 7
                        used += 1
                    elif wordNextNext in prevs:
                        tmpOffset -= 7
                        used += 1
                dayOffset += tmpOffset
            elif wordNextNext and wordNextNext in days:
                d = days.index(wordNextNext)
                tmpOffset = (d + 1) - int(today)
                used = 3
                if wordNextNextNext:
                    if wordNextNextNext in nxts:
                        tmpOffset += 7
                        used += 1
                    elif wordNextNextNext in prevs:
                        tmpOffset -= 7
                        used += 1
                dayOffset += tmpOffset
                if wordNextNextNext == "feira":
                    used += 1
        if wordNext in months:
            used -= 1
        if used > 0:

            if start - 1 > 0 and words[start - 1] in lists:
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in lists:
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
    military = False

    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""
        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word == "meio" and wordNext == "dia":
            hrAbs = 12
            used += 2
        elif word == "meia" and wordNext == "noite":
            hrAbs = 0
            used += 2
        elif word == "manha":
            if not hrAbs:
                hrAbs = 8
            used += 1
        elif word == "tarde":
            if not hrAbs:
                hrAbs = 15
            used += 1
        elif word == "meio" and wordNext == "tarde":
            if not hrAbs:
                hrAbs = 17
            used += 2
        elif word == "meio" and wordNext == "manha":
            if not hrAbs:
                hrAbs = 10
            used += 2
        elif word == "fim" and wordNext == "tarde":
            if not hrAbs:
                hrAbs = 19
            used += 2
        elif word == "fim" and wordNext == "manha":
            if not hrAbs:
                hrAbs = 11
            used += 2
        elif word == "tantas" and wordNext == "manha":
            if not hrAbs:
                hrAbs = 4
            used += 2
        elif word == "noite":
            if not hrAbs:
                hrAbs = 22
            used += 1
        # parse half an hour, quarter hour
        elif word == "hora" and \
                (wordPrev in time_indicators or wordPrevPrev in
                 time_indicators):
            if wordPrev == "meia":
                minOffset = 30
            elif wordPrev == "quarto":
                minOffset = 15
            elif wordPrevPrev == "quarto":
                minOffset = 15
                if idx > 2 and words[idx - 3] in time_indicators:
                    words[idx - 3] = ""
                words[idx - 2] = ""
            else:
                hrOffset = 1
            if wordPrevPrev in time_indicators:
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
                    elif wordNext == "manha":
                        remainder = "am"
                        used += 1
                    elif wordNext == "tarde":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "noite":
                        if 0 < int(word[0]) < 6:
                            remainder = "am"
                        else:
                            remainder = "pm"
                        used += 1
                    elif wordNext in thises and wordNextNext == "manha":
                        remainder = "am"
                        used = 2
                    elif wordNext in thises and wordNextNext == "tarde":
                        remainder = "pm"
                        used = 2
                    elif wordNext in thises and wordNextNext == "noite":
                        remainder = "pm"
                        used = 2
                    else:
                        if timeQualifier != "":
                            military = True
                            if strHH <= 12 and \
                                    (timeQualifier == "manha" or
                                     timeQualifier == "tarde"):
                                strHH += 12

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
                    if (wordNext == "pm" or
                            wordNext == "p.m." or
                            wordNext == "tarde"):
                        strHH = strNum
                        remainder = "pm"
                        used = 1
                    elif (wordNext == "am" or
                          wordNext == "a.m." or
                          wordNext == "manha"):
                        strHH = strNum
                        remainder = "am"
                        used = 1
                    elif (int(word) > 100 and
                          (
                                  wordPrev == "o" or
                                  wordPrev == "oh" or
                                  wordPrev == "zero"
                          )):
                        # 0800 hours (pronounced oh-eight-hundred)
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        military = True
                        if wordNext == "hora":
                            used += 1
                    elif (
                            wordNext == "hora" and
                            word[0] != '0' and
                            (
                                    int(word) < 100 and
                                    int(word) > 2400
                            )):
                        # ignores military time
                        # "in 3 hours"
                        hrOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1

                    elif wordNext == "minuto":
                        # "in 10 minutes"
                        minOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext == "segundo":
                        # in 5 seconds
                        secOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif int(word) > 100:
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        military = True
                        if wordNext == "hora":
                            used += 1

                    elif wordNext == "" or (
                            wordNext == "em" and wordNextNext == "ponto"):
                        strHH = word
                        strMM = 00
                        if wordNext == "em" and wordNextNext == "ponto":
                            used += 2
                            if wordNextNextNext == "tarde":
                                remainder = "pm"
                                used += 1
                            elif wordNextNextNext == "manha":
                                remainder = "am"
                                used += 1
                            elif wordNextNextNext == "noite":
                                if 0 > int(strHH) > 6:
                                    remainder = "am"
                                else:
                                    remainder = "pm"
                                used += 1

                    elif wordNext[0].isdigit():
                        strHH = word
                        strMM = wordNext
                        military = True
                        used += 1
                        if wordNextNext == "hora":
                            used += 1
                    else:
                        isTime = False

            strHH = int(strHH) if strHH else 0
            strMM = int(strMM) if strMM else 0
            strHH = strHH + 12 if (remainder == "pm" and
                                   0 < strHH < 12) else strHH
            strHH = strHH - 12 if (remainder == "am" and
                                   0 < strHH >= 12) else strHH
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

            if wordPrev == "em" or wordPrev == "ponto":
                words[words.index(wordPrev)] = ""

            if idx > 0 and wordPrev in time_indicators:
                words[idx - 1] = ""
            if idx > 1 and wordPrevPrev in time_indicators:
                words[idx - 2] = ""

            idx += used - 1
            found = True

    # check that we found a date
    if not date_found:
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

        temp = datetime.strptime(datestr, "%B %d")
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
    if (hrAbs or 0) != -1 and (minAbs or 0) != -1:
        if hrAbs is None and minAbs is None and default_time:
            hrAbs = default_time.hour
            minAbs = default_time.minute
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

    resultStr = " ".join(words)
    resultStr = ' '.join(resultStr.split())
    resultStr = pt_pruning(resultStr)
    return [extractedDate, resultStr]


def pt_pruning(text, symbols=True, accents=True, agressive=True):
    # agressive pt word pruning
    words = ["a", "o", "os", "as", "de", "dos", "das",
             "lhe", "lhes", "me", "e", "no", "nas", "na", "nos", "em", "para",
             "este",
             "esta", "deste", "desta", "neste", "nesta", "nesse",
             "nessa", "foi", "que"]
    if symbols:
        symbols = [".", ",", ";", ":", "!", "?", u"ï¿½", u"ï¿½"]
        for symbol in symbols:
            text = text.replace(symbol, "")
        text = text.replace("-", " ").replace("_", " ")
    if accents:
        accents = {"a": [u"á", u"à", u"ã", u"â"],
                   "e": [u"ê", u"è", u"é"],
                   "i": [u"í", u"ì"],
                   "o": [u"ò", u"ó"],
                   "u": [u"ú", u"ù"],
                   "c": [u"ç"]}
        for char in accents:
            for acc in accents[char]:
                text = text.replace(acc, char)
    if agressive:
        text_words = text.split(" ")
        for idx, word in enumerate(text_words):
            if word in words:
                text_words[idx] = ""
        text = " ".join(text_words)
        text = ' '.join(text.split())
    return text


def get_gender_pt(word, raw_string=""):
    word = word.rstrip("s")
    gender = None
    words = raw_string.split(" ")
    for idx, w in enumerate(words):
        if w == word and idx != 0:
            previous = words[idx - 1]
            gender = get_gender_pt(previous)
            break
    if not gender:
        if word[-1] == "a":
            gender = "f"
        if word[-1] == "o" or word[-1] == "e":
            gender = "m"
    return gender


def _convert_words_to_numbers_pt(text, short_scale=False, ordinals=False):
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
        _extract_numbers_with_text_pt(tokens, short_scale, ordinals)
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


def _extract_numbers_with_text_pt(tokens, short_scale=False,
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
        [_ReplaceableNumber]: A list of tuples, each containing a number and a
                         string.

    """
    placeholder = "<placeholder>"  # inserted to maintain correct indices
    results = []
    while True:
        to_replace = \
            _extract_number_with_text_pt(tokens, short_scale,
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


def _extract_number_with_text_pt(tokens, short_scale=False,
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
        _ReplaceableNumber

    """
    number, tokens = \
        _extract_number_with_text_pt_helper(tokens, short_scale,
                                            ordinals, fractional_numbers)
    while tokens and tokens[0].word in _PT_ARTICLES:
        tokens.pop(0)
    return ReplaceableNumber(number, tokens)


def _extract_number_with_text_pt_helper(tokens,
                                        short_scale=False, ordinals=False,
                                        fractional_numbers=True):
    """
    Helper for _extract_number_with_text_pt.

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
            _extract_fraction_with_text_pt(tokens, short_scale, ordinals)
        if fraction:
            return fraction, fraction_text

        decimal, decimal_text = \
            _extract_decimal_with_text_pt(tokens, short_scale, ordinals)
        if decimal:
            return decimal, decimal_text

    return _extract_whole_number_with_text_pt(tokens, short_scale, ordinals)


def _extract_fraction_with_text_pt(tokens, short_scale, ordinals):
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
    for c in _FRACTION_MARKER_PT:
        partitions = partition_list(tokens, lambda t: t.word == c)

        if len(partitions) == 3:
            numbers1 = \
                _extract_numbers_with_text_pt(partitions[0], short_scale,
                                              ordinals, fractional_numbers=False)
            numbers2 = \
                _extract_numbers_with_text_pt(partitions[2], short_scale,
                                              ordinals, fractional_numbers=True)

            if not numbers1 or not numbers2:
                return None, None

            # ensure first is not a fraction and second is a fraction
            num1 = numbers1[-1]
            num2 = numbers2[0]
            if num1.value >= 1 and 0 < num2.value < 1:
                return num1.value + num2.value, \
                       num1.tokens + partitions[1] + num2.tokens

    return None, None


def _extract_decimal_with_text_pt(tokens, short_scale, ordinals):
    """
    Extract decimal numbers from a string.

    This function handles text such as '2 point 5'.

    Notes:
        While this is a helper for extractnumber_pt, it also depends on
        extractnumber_pt, to parse out the components of the decimal.

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
    for c in _DECIMAL_MARKER_PT:
        partitions = partition_list(tokens, lambda t: t.word == c)

        if len(partitions) == 3:
            numbers1 = \
                _extract_numbers_with_text_pt(partitions[0], short_scale,
                                              ordinals, fractional_numbers=False)
            numbers2 = \
                _extract_numbers_with_text_pt(partitions[2], short_scale,
                                              ordinals, fractional_numbers=False)

            if not numbers1 or not numbers2:
                return None, None

            number = numbers1[-1]
            decimal = numbers2[0]

            # TODO handle number dot number number number
            if "." not in str(decimal.text):
                return number.value + float('0.' + str(decimal.value)), \
                       number.tokens + partitions[1] + decimal.tokens
    return None, None


def _extract_whole_number_with_text_pt(tokens, short_scale, ordinals):
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
        _initialize_number_data_pt(short_scale)

    number_words = []  # type: [Token]
    val = False
    prev_val = None
    next_val = None
    to_sum = []
    for idx, token in enumerate(tokens):
        if next_val:
            next_val = None
            continue

        word = token.word
        if word in _PT_ARTICLES or word in _NEGATIVES_PT:
            number_words.append(token)
            continue

        # explicit ordinals, 1º, 2º, 3ª, 4th.... Nth
        if word.endswith("º") and is_numeric(word[:-1]):
            word = word[:-1]
        elif word.endswith("ª") and is_numeric(word[:-1]):
            word = word[:-1]

        prev_word = tokens[idx - 1].word if idx > 0 else ""
        next_word = tokens[idx + 1].word if idx + 1 < len(tokens) else ""
        next_next_word = tokens[idx + 2].word if idx + 2 < len(tokens) else ""

        if word not in string_num_scale and \
                word not in _STRING_NUM_PT and \
                word not in multiplies and \
                not (ordinals and word in string_num_ordinal) and \
                not is_numeric(word) and \
                not isFractional_pt(word, short_scale=short_scale) and \
                not look_for_fractions(word.split('/')):
            words_only = [token.word for token in number_words]
            if number_words and not all([w in _PT_ARTICLES |
                                         _NEGATIVES_PT for w in words_only]):
                break
            else:
                number_words = []
                continue
        elif word not in multiplies \
                and prev_word not in multiplies \
                and not (ordinals and prev_word in string_num_ordinal) \
                and prev_word not in _NEGATIVES_PT \
                and prev_word not in _PT_ARTICLES:
            number_words = [token]
        else:
            number_words.append(token)

        # is this word already a number ?
        if is_numeric(word):
            if word.isdigit():  # doesn't work with decimals
                val = int(word)
            else:
                val = float(word)

        # is this word the name of a number ?
        if word in _STRING_NUM_PT:
            # numbers where short/long scale does not matter, < billion
            val = _STRING_NUM_PT.get(word)
        elif word in string_num_scale:
            # long/short scale matters, >= 1 billion
            val = string_num_scale.get(word)
        elif ordinals and word in string_num_ordinal:
            val = string_num_ordinal[word]
        if word not in string_num_scale and \
                word not in _STRING_NUM_PT and \
                word not in multiplies and \
                not (ordinals and word in string_num_ordinal) and \
                not is_numeric(word) and \
                not isFractional_pt(word, short_scale=short_scale) and \
                not look_for_fractions(word.split('/')):
            words_only = [token.word for token in number_words]
            if number_words and not all([w in _PT_ARTICLES |
                                         _NEGATIVES_PT for w in words_only]):
                break
            else:
                number_words = []
                continue
        elif word not in multiplies \
                and prev_word not in multiplies \
                and not (ordinals and prev_word in string_num_ordinal) \
                and prev_word not in _NEGATIVES_PT \
                and prev_word not in _PT_ARTICLES:
            number_words = [token]
        else:
            number_words.append(token)
        # is this a spoken fraction?

        # half cup
        if val is False:
            val = isFractional_pt(word, short_scale=short_scale)

        # 2 fifths
        if not ordinals:
            next_val = isFractional_pt(next_word, short_scale=short_scale)
            if next_val:
                if not val:
                    val = 1
                val = val * next_val
                number_words.append(tokens[idx + 1])

        # is this a negative number?
        # "minus two"
        if val and prev_word and prev_word in _NEGATIVES_PT:
            val = 0 - val
        # "two negative"
        if val and val > 0 and next_word and next_word in _NEGATIVE_SUFFIX_MARKER_PT:
            val = 0 - val
            number_words.append(tokens[idx + 1])
        # "two degrees negative"
        if val and val > 0 and next_next_word and next_next_word in _NEGATIVE_SUFFIX_MARKER_PT:
            val = 0 - val
            number_words.append(tokens[idx + 2])

        # let's make sure it isn't a fraction
        if not val:
            # look for fractions like "2/3"
            aPieces = word.split('/')
            if look_for_fractions(aPieces):
                val = float(aPieces[0]) / float(aPieces[1])

        else:
            # for non english speakers,  "X Y avos" means X / Y
            if prev_val and next_word in _SUFFIX_FRACTION_MARKER_PT:
                val = prev_val / val
                number_words.append(tokens[idx + 1])
                break

            # "twenty two"
            if prev_val and prev_val > val:
                to_sum.append(prev_val)
            # "hundred thousand"
            if prev_val and prev_val < val and val >= 1000:
                val *= prev_val

            prev_val = val

            # in portuguese "twenty two" can be said "twenty and two"
            if next_word in _SUM_MARKER_PT:
                number_words.append(tokens[idx + 1])
                number_words.append(tokens[idx + 2])
                next_val = extractnumber_pt(next_next_word,
                                            short_scale=short_scale,
                                            ordinals=ordinals)
                val += next_val

    if val is not None and to_sum:
        val += sum(to_sum)

    return val, number_words


def _initialize_number_data_pt(short_scale):
    """
    Generate dictionaries of words to numbers, based on scale.

    This is a helper function for _extract_whole_number.

    Args:
        short_scale boolean:

    Returns:
        (set(str), dict(str, number), dict(str, number))
        multiplies, string_num_ordinal, string_num_scale

    """
    multiplies = _MULTIPLIES_SHORT_SCALE_PT if short_scale \
        else _MULTIPLIES_LONG_SCALE_PT

    string_num_ordinal_pt = _STRING_SHORT_ORDINAL_PT if short_scale \
        else _STRING_LONG_ORDINAL_PT

    string_num_scale_pt = _SHORT_SCALE_PT if short_scale else _LONG_SCALE_PT
    string_num_scale_pt = invert_dict(string_num_scale_pt)
    string_num_scale_pt.update(generate_plurals_pt(string_num_scale_pt))

    return multiplies, string_num_ordinal_pt, string_num_scale_pt


def extractnumber_pt(text, short_scale=None, ordinals=False):
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
    # portuguese uses long_scale by default
    if short_scale is None:
        short_scale = False
    return _extract_number_with_text_pt(tokenize(text),
                                        short_scale, ordinals).value
