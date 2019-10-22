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
"""
    Parse functions for Spanish (es_ES)

    TODO: numbers greater than 999999
    TODO: date time es
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from lingua_franca.lang.parse_common import is_numeric, look_for_fractions
from lingua_franca.lang.common_data_es import _FRACTION_STRING_ES, \
    _ARTICLES_ES, _NUMBERS_ES, _FEMALE_DETERMINANTS_ES, _FEMALE_ENDINGS_ES,\
    _MALE_DETERMINANTS_ES, _MALE_ENDINGS_ES, _GENDERS_ES


def isFractional_es(input_str):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        text (str): the string to check if fractional
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    if input_str.endswith('s', -1):
        input_str = input_str[:len(input_str) - 1]  # e.g. "fifths"

    aFrac = ["medio", "tercio", "cuarto", "quinto", "sexto",
             "séptimo", "octavo", "noveno", "décimo"]

    if input_str.lower() in aFrac:
        return 1.0 / (aFrac.index(input_str) + 2)
    if input_str == "vigésimo":
        return 1.0 / 20
    if input_str == "trigésimo":
        return 1.0 / 30
    if input_str == "centésimo":
        return 1.0 / 100
    if input_str == "milésimo":
        return 1.0 / 1000
    return False


def extractnumber_es(text):
    """
    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.
    Args:
        text (str): the string to normalize
    Returns:
        (int) or (float): The value of extracted number

    """
    aWords = text.split()
    count = 0
    result = None
    while count < len(aWords):
        val = 0
        word = aWords[count]
        next_next_word = None
        if count + 1 < len(aWords):
            next_word = aWords[count + 1]
            if count + 2 < len(aWords):
                next_next_word = aWords[count + 2]
        else:
            next_word = None

        # is current word a number?
        if word in _NUMBERS_ES:
            val = _NUMBERS_ES[word]
        elif word.isdigit():  # doesn't work with decimals
            val = int(word)
        elif is_numeric(word):
            val = float(word)
        elif isFractional_es(word):
            if not result:
                result = 1
            result = result * isFractional_es(word)
            count += 1
            continue

        if not val:
            # look for fractions like "2/3"
            aPieces = word.split('/')
            # if (len(aPieces) == 2 and is_numeric(aPieces[0])
            #   and is_numeric(aPieces[1])):
            if look_for_fractions(aPieces):
                val = float(aPieces[0]) / float(aPieces[1])

        if val:
            if result is None:
                result = 0
            # handle fractions
            if next_word != "avos":
                result += val
            else:
                result = float(result) / float(val)

        if next_word is None:
            break

        # number word and fraction
        ands = ["y"]
        if next_word in ands:
            zeros = 0
            if result is None:
                count += 1
                continue
            newWords = aWords[count + 2:]
            newText = ""
            for word in newWords:
                newText += word + " "

            afterAndVal = extractnumber_es(newText[:-1])
            if afterAndVal:
                if result < afterAndVal or result < 20:
                    while afterAndVal > 1:
                        afterAndVal = afterAndVal / 10.0
                    for word in newWords:
                        if word == "cero" or word == "0":
                            zeros += 1
                        else:
                            break
                for _ in range(0, zeros):
                    afterAndVal = afterAndVal / 10.0
                result += afterAndVal
                break
        elif next_next_word is not None:
            if next_next_word in ands:
                newWords = aWords[count + 3:]
                newText = ""
                for word in newWords:
                    newText += word + " "
                afterAndVal = extractnumber_es(newText[:-1])
                if afterAndVal:
                    if result is None:
                        result = 0
                    result += afterAndVal
                    break

        decimals = ["punto", "coma", ".", ","]
        if next_word in decimals:
            zeros = 0
            newWords = aWords[count + 2:]
            newText = ""
            for word in newWords:
                newText += word + " "
            for word in newWords:
                if word == "cero" or word == "0":
                    zeros += 1
                else:
                    break
            afterDotVal = str(extractnumber_es(newText[:-1]))
            afterDotVal = zeros * "0" + afterDotVal
            result = float(str(result) + "." + afterDotVal)
            break
        count += 1

    if result is None:
        return False

    # Return the $str with the number related words removed
    # (now empty strings, so strlen == 0)
    # aWords = [word for word in aWords if len(word) > 0]
    # text = ' '.join(aWords)
    if "." in str(result):
        integer, dec = str(result).split(".")
        # cast float to int
        if dec == "0":
            result = int(integer)

    return result

# TODO: specify lang at the end on function names
def es_number_parse(words, i):
    def es_cte(i, s):
        if i < len(words) and s == words[i]:
            return s, i + 1
        return None

    def es_number_word(i, mi, ma):
        if i < len(words):
            v = _NUMBERS_ES.get(words[i])
            if v and v >= mi and v <= ma:
                return v, i + 1
        return None

    def es_number_1_99(i):
        r1 = es_number_word(i, 1, 29)
        if r1:
            return r1

        r1 = es_number_word(i, 30, 90)
        if r1:
            v1, i1 = r1
            r2 = es_cte(i1, "y")
            if r2:
                i2 = r2[1]
                r3 = es_number_word(i2, 1, 9)
                if r3:
                    v3, i3 = r3
                    return v1 + v3, i3
            return r1
        return None

    def es_number_1_999(i):
        # [2-9]cientos [1-99]?
        r1 = es_number_word(i, 100, 900)
        if r1:
            v1, i1 = r1
            r2 = es_number_1_99(i1)
            if r2:
                v2, i2 = r2
                return v1 + v2, i2
            else:
                return r1

        # [1-99]
        r1 = es_number_1_99(i)
        if r1:
            return r1

        return None

    def es_number(i):
        # check for cero
        r1 = es_number_word(i, 0, 0)
        if r1:
            return r1

        # check for [1-999] (mil [0-999])?
        r1 = es_number_1_999(i)
        if r1:
            v1, i1 = r1
            r2 = es_cte(i1, "mil")
            if r2:
                i2 = r2[1]
                r3 = es_number_1_999(i2)
                if r3:
                    v3, i3 = r3
                    return v1 * 1000 + v3, i3
                else:
                    return v1 * 1000, i2
            else:
                return r1
        return None

    return es_number(i)


def normalize_es(text, remove_articles):
    """ ES string normalization """

    words = text.split()  # this also removed extra spaces
    normalized = ""
    # Contractions are not common in ES

    # Convert numbers into digits, e.g. "dois" -> "2"
    normalized = ""
    i = 0
    while i < len(words):
        word = words[i]
        # remove articles
        if remove_articles and word in _ARTICLES_ES:
            i += 1
            continue

        # Convert numbers into digits
        r = es_number_parse(words, i)
        if r:
            v, i = r
            normalized += " " + str(v)
            continue

        # NOTE temporary , handle some numbers above >999
        if word in _NUMBERS_ES:
            word = str(_NUMBERS_ES[word])
        # end temporary

        normalized += " " + word
        i += 1
    # some articles in es_ES can not be removed, but many words can
    # this is experimental and some meaning may be lost
    # maybe agressive should default to False
    # only usage will tell, as a native speaker this seems reasonable
    return es_pruning(normalized[1:], agressive=remove_articles)


def extract_datetime_es(input_str, currentDate, default_time):
    def clean_string(s):
        # cleans the input string of unneeded punctuation and capitalization
        # among other things
        symbols = [".", ",", ";", "?", "!", "º", "ª"]
        noise_words = ["lo", "los", "la", "las", "de", "para"]

        for word in symbols:
            s = s.replace(word, "")
        for word in noise_words:
            s = s.replace(" " + word + " ", " ")
        # TODO: need to replace "ñ" as well?
        s = s.lower().replace(
            "á",
            "a").replace(
            "é",
            "e").replace(
            "í",
            "i").replace(
            "ó",
            "o").replace(
            "ú",
            "u").replace(
            "-",
            " ").replace(
            "_",
            "")
        # handle synonims and equivalents, "tomorrow early = tomorrow morning
        synonims = {"mañana": ["matutino", "temprano", "pronto"],
                    "tarde": ["atardecer", "tarde"],
                    "noche": ["nocturno", "anochecer"],
                    "todos": ["al", "hacia"],
                    "en": ["de"]}
        for syn in synonims:
            for word in synonims[syn]:
                s = s.replace(" " + word + " ", " " + syn + " ")
        # relevant plurals, cant just extract all s in es
        wordlist = ["mañanas", "noches", "tardes", "dias", "semanas", "años",
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
    timeQualifiersList = ['mañana', 'tarde', 'noche']
    # TODO: need to remove "la" from the following?
    # There are also other compound time indicators like
    # "después de", "pasadas las", "pasada la", "dentro de", etc
    time_indicators = ["por", "las", "la", "esta", "pasada", "tras", "estas",
                       "desde", "dia", "hora"]
    days = ['lunes', 'martes', 'miercoles',
            'jueves', 'viernes', 'sabado', 'domingo']
    months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre',
              'diciembre']
    monthsShort = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago',
                   'sep', 'oct', 'nov', 'dic']
    nexts = ["proximo", "proxima"]
    # TODO: most used suffix is "que viene"
    suffix_nexts = ["siguiente", "subsiguiente"]
    lasts = ["ultimo", "ultima"]
    suffix_lasts = ["pasada", "pasado", "anterior", "antes"]
    nxts = ["después", "siguiente", "proxima", "proximo"]
    prevs = ["antes", "ante", "previa", "previamente", "anterior"]
    # TODO: there are many compound particles, like
    # "desde aquí" "después de", "a partir de" etc
    froms = ["partir", "en", "para", "despues","por", "proxima", 
             "proximo", "de"]
    thises = ["este", "esta", "ese", "esa", "esos", "esas", "estos", "estas"]
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
        elif word == "hoy" and not fromFlag:
            dayOffset = 0
            used += 1
        elif word == "mañana" and not fromFlag:
            dayOffset = 1
            used += 1
        elif word == "ayer" and not fromFlag:
            dayOffset -= 1
            used += 1
        # "before yesterday" and "before before yesterday"
        elif (word == "anteayer" or
              (word == "ante" and wordNext == "ayer")) and not fromFlag:
            dayOffset -= 2
            used += 1
            if wordNext == "ayer":
                used += 1
        elif word == "ante" and wordNext == "ante" and wordNextNext == \
                "ayer" and not fromFlag:
            dayOffset -= 3
            used += 3
        elif word == "anteanteayer" and not fromFlag:
            dayOffset -= 3
            used += 1
        # day after tomorrow
        elif word == "pasado" and wordNext == "mañana" and not fromFlag:
            dayOffset += 2
            used = 2
        # day before yesterday
        elif word == "ante" and wordNext == "ayer" and not fromFlag:
            dayOffset -= 2
            used = 2
        # parse 5 days, 10 weeks, last week, next week, week after
        elif word == "dia":
            if wordNext == "pasado" or wordNext == "antes":
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
        elif word == "año" and not fromFlag:
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
            if wordNext == "día":
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
                # 13 mayo
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
                # mayo 13
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordPrevPrev and wordPrevPrev[0].isdigit():
                # 13 dia mayo
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
                # mayo dia 13
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
        validFollowups.append("hoy")
        validFollowups.append("mañana")
        validFollowups.append("ayer")
        validFollowups.append("anteayer")
        validFollowups.append("ahora")
        validFollowups.append("ya")
        validFollowups.append("ante")

        # TODO debug word "pasado" that one is failing for some reason
        if word in froms and wordNext in validFollowups:

            if not (wordNext == "mañana" and wordNext == "ayer") and not (
                    word == "pasado" or word == "antes" or word == "en"):
                used = 2
                fromFlag = True
            if wordNext == "mañana" and word != "pasado":
                dayOffset += 1
            elif wordNext == "ayer":
                dayOffset -= 1
            elif wordNext == "anteayer":
                dayOffset -= 2
            elif wordNext == "ante" and wordNextNext == "ayer":
                dayOffset -= 2
            elif (wordNext == "ante" and wordNextNext == "ante" and
                  wordNextNextNext == "ayer"):
                dayOffset -= 3
            elif wordNext in days:
                d = days.index(wordNext)
                tmpOffset = (d + 1) - int(today)
                used = 2
                if wordNextNext == "día":
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
                if wordNextNextNext == "día":
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
    
    # TODO: Is this necessary?
    # military = False

    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        wordNextNextNext = words[idx + 3] if idx + 3 < len(words) else ""
        # parse noon, midnight, morning, afternoon, evening
        # TODO: 
        used = 0
        # if word == 'mediodía':
        #     hrAbs = 12
        #     used += 1
        # elif word == 'medianoche':
        #     hrAbs = 0
        #     used += 1
        # if word == 'medio' and wordNext == 'día':
        #     hrAbs = 12
        #     used += 2
        # elif word == 'media' and wordNext == 'noche':
        #     hrAbs = 0
        #     used += 2
        # elif word == 'mañana' and wordPrev == 'la':
        #     if not hrAbs:
        #         hrAbs = 8
        #     used += 1
        #     if wordNext and wordNext[0].isdigit():  # mattina alle 5
        #         hrAbs = int(wordNext)
        #         used += 1
        # elif word == 'tarde':
        #     if not hrAbs:
        #         hrAbs = 15
        #     used += 1
        #     if wordNext and wordNext[0].isdigit():  # pomeriggio alle 5
        #         hrAbs = int(wordNext)
        #         used += 1
        #         if (hrAbs or 0) < 12:
        #             hrAbs = (hrAbs or 0) + 12
        # elif word == 'noche':
        #     if not hrAbs:
        #         hrAbs = 19
        #     used += 1
        #     if wordNext and wordNext[0].isdigit() \
        #        and ':' not in wordNext:
        #         hrAbs = int(wordNext)
        #         used += 1
        #         if (hrAbs or 0) < 12:
        #             hrAbs = (hrAbs or 0) + 12


        if word == "medio" and wordNext == "día":
            hrAbs = 12
            used += 2
        elif word == "media" and wordNext == "noche":
            hrAbs = 0
            used += 2
        elif word == "mañana" and wordPrev == "la":
            if not hrAbs:
                hrAbs = 8
            used += 2
        elif word == "tarde":
            if not hrAbs:
                hrAbs = 15
            used += 1
        elif word == "media" and wordNext == "tarde":
            if not hrAbs:
                hrAbs = 17
            used += 2
        elif word == "media" and wordNext == "mañana":
            if not hrAbs:
                hrAbs = 10
            used += 2
        elif word == "tarde" and wordNext == "noche":
            if not hrAbs:
                hrAbs = 19
            used += 2
        # elif word == "fim" and wordNext == "manha":
        #     if not hrAbs:
        #         hrAbs = 11
        #     used += 2
        elif word == "madrugada":
            if not hrAbs:
                hrAbs = 4
            used += 1
        elif word == "noche":
            if not hrAbs:
                hrAbs = 22
            used += 1
        # parse half an hour, quarter hour
        elif word == "hora" and \
                (wordPrev in time_indicators or wordPrevPrev in
                 time_indicators):
            if wordPrev == "media":
                minOffset = 30
            elif wordPrev == "cuarto":
                minOffset = 15
            elif wordPrevPrev == "cuarto":
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
                    elif wordNext == "mañana":
                        remainder = "am"
                        used += 1
                    elif wordNext == "tarde":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "noche":
                        if 0 < int(word[0]) < 6:
                            remainder = "am"
                        else:
                            remainder = "pm"
                        used += 1
                    elif wordNext in thises and wordNextNext == "mañana":
                        remainder = "am"
                        used = 2
                    elif wordNext in thises and wordNextNext == "tarde":
                        remainder = "pm"
                        used = 2
                    elif wordNext in thises and wordNextNext == "noche":
                        remainder = "pm"
                        used = 2
                    else:
                        if timeQualifier != "":
                            # military = True
                            if strHH <= 12 and \
                                    (timeQualifier == "mañana" or
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
                          wordNext == "mañana"):
                        strHH = strNum
                        remainder = "am"
                        used = 1
                    elif (int(word) > 100 and
                          (
                                  wordPrev == "o" or
                                  wordPrev == "oh" or
                                  wordPrev == "cero"
                          )):
                        # 0800 hours (pronounced oh-eight-hundred)
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        # military = True
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
                        # military = True
                        if wordNext == "hora":
                            used += 1

                    elif wordNext == "" or (
                            wordNext == "en" and wordNextNext == "punto"):
                        strHH = word
                        strMM = 00
                        if wordNext == "en" and wordNextNext == "punto":
                            used += 2
                            if wordNextNextNext == "tarde":
                                remainder = "pm"
                                used += 1
                            elif wordNextNextNext == "mañana":
                                remainder = "am"
                                used += 1
                            elif wordNextNextNext == "noche":
                                if 0 > int(strHH) > 6:
                                    remainder = "am"
                                else:
                                    remainder = "pm"
                                used += 1

                    elif wordNext[0].isdigit():
                        strHH = word
                        strMM = wordNext
                        # military = True
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

            if wordPrev == "en" or wordPrev == "punto":
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
    resultStr = es_pruning(resultStr)
    return [extractedDate, resultStr]


def es_pruning(text, symbols=True, accents=True, agressive=True):
    # agressive es word pruning
    words = ["la", "lo", "los", "las", "de", "le", "les", "me", "nos",
             "para", "este", "esta", "estos", "estas", "era", "eran", "quién"]
    if symbols:
        symbols = [".", ",", ";", ":", "!", "?", u"ï¿½", u"ï¿½"]
        for symbol in symbols:
            text = text.replace(symbol, "")
        text = text.replace("-", " ").replace("_", " ")
    if accents:
        # TODO: Should I put here "n": "ñ"??
        accents = {"a": "á",
                   "e": "é",
                   "i": "í",
                   "o": "ó",
                   "u": "ú",
                   }
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


def get_gender_es(word, text=""):
    # parse gender taking context into account
    word = word.lower()
    words = text.lower().split(" ")
    for idx, w in enumerate(words):
        if w == word and idx != 0:
            # in spanish usually the previous word (a determinant)
            # assigns gender to the next word
            previous = words[idx - 1].lower()
            if previous in _MALE_DETERMINANTS_ES:
                return "m"
            elif previous in _FEMALE_DETERMINANTS_ES:
                return "f"

    # get gender using only the individual word
    # see if this word has the gender defined
    if word in _GENDERS_ES:
        return _GENDERS_ES[word]
    singular = word.rstrip("s")
    if singular in _GENDERS_ES:
        return _GENDERS_ES[singular]
    # in spanish the last vowel usually defines the gender of a word
    # the gender of the determinant takes precedence over this rule
    for end_str in _FEMALE_ENDINGS_ES:
        if word.endswith(end_str):
            return "f"
    for end_str in _MALE_ENDINGS_ES:
        if word.endswith(end_str):
            return "m"
    return None
