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
from collections import namedtuple
import re
from enum import Enum


class Normalizer:
    """
    individual languages may subclass this if needed

    normalize_XX should pass a valid config read from json
    """
    _default_config = {}

    def __init__(self, config=None):
        self.config = config or self._default_config

    @staticmethod
    def tokenize(utterance):
        # Split things like 12%
        utterance = re.sub(r"([0-9]+)([\%])", r"\1 \2", utterance)
        # Split thins like #1
        utterance = re.sub(r"(\#)([0-9]+\b)", r"\1 \2", utterance)
        return utterance.split()

    @property
    def should_lowercase(self):
        return self.config.get("lowercase", False)

    @property
    def should_numbers_to_digits(self):
        return self.config.get("numbers_to_digits", True)

    @property
    def should_expand_contractions(self):
        return self.config.get("expand_contractions", True)

    @property
    def should_remove_symbols(self):
        return self.config.get("remove_symbols", False)

    @property
    def should_remove_accents(self):
        return self.config.get("remove_accents", False)

    @property
    def should_remove_articles(self):
        return self.config.get("remove_articles", False)

    @property
    def should_remove_stopwords(self):
        return self.config.get("remove_stopwords", False)

    @property
    def contractions(self):
        return self.config.get("contractions", {})

    @property
    def word_replacements(self):
        return self.config.get("word_replacements", {})

    @property
    def number_replacements(self):
        return self.config.get("number_replacements", {})

    @property
    def accents(self):
        return self.config.get("accents",
                               {"á": "a", "à": "a", "ã": "a", "â": "a",
                                "é": "e", "è": "e", "ê": "e", "ẽ": "e",
                                "í": "i", "ì": "i", "î": "i", "ĩ": "i",
                                "ò": "o", "ó": "o", "ô": "o", "õ": "o",
                                "ú": "u", "ù": "u", "û": "u", "ũ": "u",
                                "Á": "A", "À": "A", "Ã": "A", "Â": "A",
                                "É": "E", "È": "E", "Ê": "E", "Ẽ": "E",
                                "Í": "I", "Ì": "I", "Î": "I", "Ĩ": "I",
                                "Ò": "O", "Ó": "O", "Ô": "O", "Õ": "O",
                                "Ú": "U", "Ù": "U", "Û": "U", "Ũ": "U"
                                })

    @property
    def stopwords(self):
        return self.config.get("stopwords", [])

    @property
    def articles(self):
        return self.config.get("articles", [])

    @property
    def symbols(self):
        return self.config.get("symbols",
                               [";", "_", "!", "?", "<", ">",
                                "|", "(", ")", "=", "[", "]", "{",
                                "}", "»", "«", "*", "~", "^", "`"])

    def expand_contractions(self, utterance):
        """ Expand common contractions, e.g. "isn't" -> "is not" """
        words = self.tokenize(utterance)
        for idx, w in enumerate(words):
            if w in self.contractions:
                words[idx] = self.contractions[w]
        utterance = " ".join(words)
        return utterance

    def numbers_to_digits(self, utterance):
        words = self.tokenize(utterance)
        for idx, w in enumerate(words):
            if w in self.number_replacements:
                words[idx] = self.number_replacements[w]
        utterance = " ".join(words)
        return utterance

    def remove_articles(self, utterance):
        words = self.tokenize(utterance)
        for idx, w in enumerate(words):
            if w in self.articles:
                words[idx] = ""
        utterance = " ".join(words)
        return utterance

    def remove_stopwords(self, utterance):
        words = self.tokenize(utterance)
        for idx, w in enumerate(words):
            if w in self.stopwords:
                words[idx] = ""
        # if words[-1] == '-':
        #    words = words[:-1]
        utterance = " ".join(words)
        # Remove trailing whitespaces from utterance along with orphaned
        # hyphens, more characters may be added later
        utterance = re.sub(r'- *$', '', utterance)
        return utterance

    def remove_symbols(self, utterance):
        for s in self.symbols:
            utterance = utterance.replace(s, " ")
        return utterance

    def remove_accents(self, utterance):
        for s in self.accents:
            utterance = utterance.replace(s, self.accents[s])
        return utterance

    def replace_words(self, utterance):
        words = self.tokenize(utterance)
        for idx, w in enumerate(words):
            if w in self.word_replacements:
                words[idx] = self.word_replacements[w]
        utterance = " ".join(words)
        return utterance

    def normalize(self, utterance="", remove_articles=None):
        # mutations
        if self.should_lowercase:
            utterance = utterance.lower()
        if self.should_expand_contractions:
            utterance = self.expand_contractions(utterance)
        if self.should_numbers_to_digits:
            utterance = self.numbers_to_digits(utterance)
        utterance = self.replace_words(utterance)

        # removals
        if self.should_remove_symbols:
            utterance = self.remove_symbols(utterance)
        if self.should_remove_accents:
            utterance = self.remove_accents(utterance)
        # TODO deprecate remove_articles param, backwards compat
        if remove_articles is not None and remove_articles:
            utterance = self.remove_articles(utterance)
        elif self.should_remove_articles:
            utterance = self.remove_articles(utterance)
        if self.should_remove_stopwords:
            utterance = self.remove_stopwords(utterance)
        # remove extra spaces
        utterance = " ".join([w for w in utterance.split(" ") if w])
        return utterance


# Token is intended to be used in the number processing functions in
# this module. The parsing requires slicing and dividing of the original
# text. To ensure things parse correctly, we need to know where text came
# from in the original input, hence this nametuple.
Token = namedtuple('Token', 'word index')


class ReplaceableNumber:
    """
    Similar to Token, this class is used in number parsing.

    Once we've found a number in a string, this class contains all
    the info about the value, and where it came from in the original text.
    In other words, it is the text, and the number that can replace it in
    the string.
    """

    def __init__(self, value, tokens: [Token]):
        self.value = value
        self.tokens = tokens

    def __bool__(self):
        return bool(self.value is not None and self.value is not False)

    @property
    def start_index(self):
        return self.tokens[0].index

    @property
    def end_index(self):
        return self.tokens[-1].index

    @property
    def text(self):
        return ' '.join([t.word for t in self.tokens])

    def __setattr__(self, key, value):
        try:
            getattr(self, key)
        except AttributeError:
            super().__setattr__(key, value)
        else:
            raise Exception("Immutable!")

    def __str__(self):
        return "({v}, {t})".format(v=self.value, t=self.tokens)

    def __repr__(self):
        return "{n}({v}, {t})".format(n=self.__class__.__name__, v=self.value,
                                      t=self.tokens)


def tokenize(text):
    """
    Generate a list of token object, given a string.
    Args:
        text str: Text to tokenize.

    Returns:
        [Token]

    """
    return [Token(word, index)
            for index, word in enumerate(Normalizer.tokenize(text))]


def partition_list(items, split_on):
    """
    Partition a list of items.

    Works similarly to str.partition

    Args:
        items:
        split_on callable:
            Should return a boolean. Each item will be passed to
            this callable in succession, and partitions will be
            created any time it returns True.

    Returns:
        [[any]]

    """
    splits = []
    current_split = []
    for item in items:
        if split_on(item):
            splits.append(current_split)
            splits.append([item])
            current_split = []
        else:
            current_split.append(item)
    splits.append(current_split)
    return list(filter(lambda x: len(x) != 0, splits))


def invert_dict(original):
    """
    Produce a dictionary with the keys and values
    inverted, relative to the dict passed in.

    Args:
        original dict: The dict like object to invert

    Returns:
        dict

    """
    return {value: key for key, value in original.items()}


def is_numeric(input_str):
    """
    Takes in a string and tests to see if it is a number.
    Args:
        text (str): string to test if a number
    Returns:
        (bool): True if a number, else False

    """

    try:
        float(input_str)
        return True
    except ValueError:
        return False


def look_for_fractions(split_list):
    """"
    This function takes a list made by fraction & determines if a fraction.

    Args:
        split_list (list): list created by splitting on '/'
    Returns:
        (bool): False if not a fraction, otherwise True

    """

    if len(split_list) == 2:
        if is_numeric(split_list[0]) and is_numeric(split_list[1]):
            return True

    return False


def extract_numbers_generic(text, pronounce_handler, extract_handler,
                            short_scale=True, ordinals=False):
    """
        Takes in a string and extracts a list of numbers.
        Language agnostic, per language parsers need to be provided

    Args:
        text (str): the string to extract a number from
        pronounce_handler (function): function that pronounces a number
        extract_handler (function): function that extracts the last number
        present in a string
        short_scale (bool): Use "short scale" or "long scale" for large
            numbers -- over a million.  The default is short scale, which
            is now common in most English speaking countries.
            See https://en.wikipedia.org/wiki/Names_of_large_numbers
        ordinals (bool): consider ordinal numbers, e.g. third=3 instead of 1/3
    Returns:
        list: list of extracted numbers as floats
    """
    numbers = []
    normalized = text
    extract = extract_handler(normalized, short_scale, ordinals)
    to_parse = normalized
    while extract:
        numbers.append(extract)
        prev = to_parse
        num_txt = pronounce_handler(extract)
        extract = str(extract)
        if extract.endswith(".0"):
            extract = extract[:-2]

        # handle duplicate occurences, replace last one only
        def replace_right(source, target, replacement, replacements=None):
            return replacement.join(source.rsplit(target, replacements))

        normalized = replace_right(normalized, num_txt, extract, 1)
        # last biggest number was replaced, recurse to handle cases like
        # test one two 3
        to_parse = replace_right(to_parse, num_txt, extract, 1)
        to_parse = replace_right(to_parse, extract, " ", 1)
        if to_parse == prev:
            # avoid infinite loops, occasionally pronounced number may be
            # different from extracted text,
            # ie pronounce(0.5) != half and extract(half) == 0.5
            extract = False
            # TODO fix this
        else:
            extract = extract_handler(to_parse, short_scale, ordinals)
    numbers.reverse()
    return numbers


class DurationResolution(Enum):
    TIMEDELTA = 0
    RELATIVEDELTA = 1
    RELATIVEDELTA_STRICT = 1
    RELATIVEDELTA_FALLBACK = 2
    RELATIVEDELTA_APPROXIMATE = 3
    TOTAL_SECONDS = 4
    TOTAL_MICROSECONDS = 5
    TOTAL_MILLISECONDS = 6
    TOTAL_MINUTES = 7
    TOTAL_HOURS = 8
    TOTAL_DAYS = 9
    TOTAL_WEEKS = 10
    TOTAL_MONTHS = 11
    TOTAL_YEARS = 12
    TOTAL_DECADES = 13
    TOTAL_CENTURIES = 14
    TOTAL_MILLENNIUMS = 15


class DateTimeResolution(Enum):
    # absolute units
    MICROSECOND = 0
    MILLISECOND = 1
    SECOND = 2
    MINUTE = 3
    HOUR = 4

    DAY = 5
    WEEKEND = 6
    WEEK = 7
    MONTH = 8
    YEAR = 9
    DECADE = 10
    CENTURY = 11
    MILLENNIUM = 12

    SEASON = 13
    SPRING = 14
    FALL = 15
    WINTER = 16
    SUMMER = 17

    # {unit} of {resolution}
    MICROSECOND_OF_MILLISECOND = 18
    MICROSECOND_OF_SECOND = 19
    MICROSECOND_OF_MINUTE = 20
    MICROSECOND_OF_HOUR = 21
    MICROSECOND_OF_DAY = 22
    MICROSECOND_OF_WEEKEND = 23
    MICROSECOND_OF_WEEK = 24
    MICROSECOND_OF_MONTH = 25
    MICROSECOND_OF_YEAR = 26
    MICROSECOND_OF_DECADE = 27
    MICROSECOND_OF_CENTURY = 28
    MICROSECOND_OF_MILLENNIUM = 29

    MICROSECOND_OF_SEASON = 30
    MICROSECOND_OF_SPRING = 31
    MICROSECOND_OF_FALL = 32
    MICROSECOND_OF_WINTER = 33
    MICROSECOND_OF_SUMMER = 34

    MILLISECOND_OF_SECOND = 35
    MILLISECOND_OF_MINUTE = 36
    MILLISECOND_OF_HOUR = 37
    MILLISECOND_OF_DAY = 38
    MILLISECOND_OF_WEEKEND = 39
    MILLISECOND_OF_WEEK = 40
    MILLISECOND_OF_MONTH = 41
    MILLISECOND_OF_YEAR = 42
    MILLISECOND_OF_DECADE = 43
    MILLISECOND_OF_CENTURY = 44
    MILLISECOND_OF_MILLENNIUM = 45

    MILLISECOND_OF_SEASON = 46
    MILLISECOND_OF_SPRING = 47
    MILLISECOND_OF_FALL = 48
    MILLISECOND_OF_WINTER = 49
    MILLISECOND_OF_SUMMER = 50

    SECOND_OF_MINUTE = 51
    SECOND_OF_HOUR = 52
    SECOND_OF_DAY = 53
    SECOND_OF_WEEKEND = 54
    SECOND_OF_WEEK = 55
    SECOND_OF_MONTH = 56
    SECOND_OF_YEAR = 57
    SECOND_OF_DECADE = 58
    SECOND_OF_CENTURY = 59
    SECOND_OF_MILLENNIUM = 60

    SECOND_OF_SEASON = 61
    SECOND_OF_SPRING = 62
    SECOND_OF_FALL = 63
    SECOND_OF_WINTER = 64
    SECOND_OF_SUMMER = 65

    MINUTE_OF_HOUR = 66
    MINUTE_OF_DAY = 67
    MINUTE_OF_WEEKEND = 68
    MINUTE_OF_WEEK = 69
    MINUTE_OF_MONTH = 70
    MINUTE_OF_YEAR = 71
    MINUTE_OF_DECADE = 72
    MINUTE_OF_CENTURY = 73
    MINUTE_OF_MILLENNIUM = 74

    MINUTE_OF_SEASON = 75
    MINUTE_OF_SPRING = 76
    MINUTE_OF_FALL = 77
    MINUTE_OF_WINTER = 78
    MINUTE_OF_SUMMER = 79

    HOUR_OF_DAY = 80
    HOUR_OF_WEEKEND = 81
    HOUR_OF_WEEK = 82
    HOUR_OF_MONTH = 83
    HOUR_OF_YEAR = 84
    HOUR_OF_DECADE = 85
    HOUR_OF_CENTURY = 86
    HOUR_OF_MILLENNIUM = 87

    HOUR_OF_SEASON = 88
    HOUR_OF_SPRING = 89
    HOUR_OF_FALL = 90
    HOUR_OF_WINTER = 91
    HOUR_OF_SUMMER = 92

    DAY_OF_WEEKEND = 93
    DAY_OF_WEEK = 94
    DAY_OF_MONTH = 95
    DAY_OF_YEAR = 96
    DAY_OF_DECADE = 97
    DAY_OF_CENTURY = 98
    DAY_OF_MILLENNIUM = 99

    DAY_OF_SEASON = 100
    DAY_OF_SPRING = 101
    DAY_OF_FALL = 102
    DAY_OF_WINTER = 103
    DAY_OF_SUMMER = 104

    WEEKEND_OF_MONTH = 105
    WEEKEND_OF_YEAR = 106
    WEEKEND_OF_DECADE = 107
    WEEKEND_OF_CENTURY = 108
    WEEKEND_OF_MILLENNIUM = 109

    WEEKEND_OF_SEASON = 110
    WEEKEND_OF_SPRING = 111
    WEEKEND_OF_FALL = 112
    WEEKEND_OF_WINTER = 113
    WEEKEND_OF_SUMMER = 114

    WEEK_OF_MONTH = 115
    WEEK_OF_YEAR = 116
    WEEK_OF_CENTURY = 117
    WEEK_OF_DECADE = 118
    WEEK_OF_MILLENNIUM = 119

    WEEK_OF_SEASON = 120
    WEEK_OF_SPRING = 121
    WEEK_OF_FALL = 122
    WEEK_OF_WINTER = 123
    WEEK_OF_SUMMER = 124

    MONTH_OF_YEAR = 125
    MONTH_OF_DECADE = 126
    MONTH_OF_CENTURY = 127
    MONTH_OF_MILLENNIUM = 128

    MONTH_OF_SEASON = 129
    MONTH_OF_SPRING = 130
    MONTH_OF_FALL = 131
    MONTH_OF_WINTER = 132
    MONTH_OF_SUMMER = 133

    YEAR_OF_DECADE = 134
    YEAR_OF_CENTURY = 135
    YEAR_OF_MILLENNIUM = 136

    DECADE_OF_CENTURY = 137
    DECADE_OF_MILLENNIUM = 138

    CENTURY_OF_MILLENNIUM = 139

    SEASON_OF_YEAR = 140
    SEASON_OF_DECADE = 141
    SEASON_OF_CENTURY = 142
    SEASON_OF_MILLENNIUM = 143

    SPRING_OF_YEAR = 144
    SPRING_OF_DECADE = 145
    SPRING_OF_CENTURY = 146
    SPRING_OF_MILLENNIUM = 147

    FALL_OF_YEAR = 148
    FALL_OF_DECADE = 149
    FALL_OF_CENTURY = 150
    FALL_OF_MILLENNIUM = 151

    WINTER_OF_YEAR = 152
    WINTER_OF_DECADE = 153
    WINTER_OF_CENTURY = 154
    WINTER_OF_MILLENNIUM = 155

    SUMMER_OF_YEAR = 156
    SUMMER_OF_DECADE = 157
    SUMMER_OF_CENTURY = 158
    SUMMER_OF_MILLENNIUM = 159

    # Special reference dates
    # number of days since 1 January 4713 BC, 12:00:00 (UTC).
    JULIAN_MICROSECOND = 160
    JULIAN_MILLISECOND = 161
    JULIAN_SECOND = 162
    JULIAN_MINUTE = 163
    JULIAN_HOUR = 164
    JULIAN_DAY = 165
    JULIAN_WEEK = 166
    JULIAN_WEEKEND = 167
    JULIAN_MONTH = 168
    JULIAN_YEAR = 169
    JULIAN_DECADE = 170
    JULIAN_CENTURY = 171
    JULIAN_MILLENNIUM = 172

    JULIAN_SEASON = 173
    JULIAN_SPRING = 174
    JULIAN_FALL = 175
    JULIAN_WINTER = 176
    JULIAN_SUMMER = 177

    # Julian day corrected for differences  in the Earth's position with
    # respect to the Sun.
    HELIOCENTRIC_JULIAN_MICROSECOND = 178
    HELIOCENTRIC_JULIAN_MILLISECOND = 179
    HELIOCENTRIC_JULIAN_SECOND = 180
    HELIOCENTRIC_JULIAN_MINUTE = 181
    HELIOCENTRIC_JULIAN_HOUR = 182
    HELIOCENTRIC_JULIAN_DAY = 183
    HELIOCENTRIC_JULIAN_WEEK = 184
    HELIOCENTRIC_JULIAN_WEEKEND = 185
    HELIOCENTRIC_JULIAN_MONTH = 186
    HELIOCENTRIC_JULIAN_YEAR = 187
    HELIOCENTRIC_JULIAN_DECADE = 188
    HELIOCENTRIC_JULIAN_CENTURY = 189
    HELIOCENTRIC_JULIAN_MILLENNIUM = 190

    HELIOCENTRIC_JULIAN_SEASON = 191
    HELIOCENTRIC_JULIAN_SPRING = 192
    HELIOCENTRIC_JULIAN_FALL = 193
    HELIOCENTRIC_JULIAN_WINTER = 194
    HELIOCENTRIC_JULIAN_SUMMER = 195

    # Julian day corrected for differences in the Earth's position with
    # respect to the barycentre of the Solar System.
    BARYCENTRIC__JULIAN_MICROSECOND = 196
    BARYCENTRIC__JULIAN_MILLISECOND = 197
    BARYCENTRIC__JULIAN_SECOND = 198
    BARYCENTRIC__JULIAN_MINUTE = 199
    BARYCENTRIC__JULIAN_HOUR = 200
    BARYCENTRIC_JULIAN_DAY = 201
    BARYCENTRIC_JULIAN_WEEK = 202
    BARYCENTRIC_JULIAN_WEEKEND = 203
    BARYCENTRIC_JULIAN_MONTH = 204
    BARYCENTRIC_JULIAN_YEAR = 205
    BARYCENTRIC_JULIAN_DECADE = 206
    BARYCENTRIC_JULIAN_CENTURY = 207
    BARYCENTRIC_JULIAN_MILLENNIUM = 208

    BARYCENTRIC_JULIAN_SEASON = 209
    BARYCENTRIC_JULIAN_SPRING = 210
    BARYCENTRIC_JULIAN_FALL = 211
    BARYCENTRIC_JULIAN_WINTER = 212
    BARYCENTRIC_JULIAN_SUMMER = 213

    # Unix time, number of seconds elapsed since 1 January 1970, 00:00:00 (
    # UTC).
    UNIX_MICROSECOND = 214
    UNIX_MILLISECOND = 215
    UNIX_SECOND = 216
    UNIX_MINUTE = 217
    UNIX_HOUR = 218
    UNIX_DAY = 219
    UNIX_WEEK = 220
    UNIX_WEEKEND = 221
    UNIX_MONTH = 222
    UNIX_YEAR = 223
    UNIX_DECADE = 224
    UNIX_CENTURY = 225
    UNIX_MILLENNIUM = 226

    UNIX_SEASON = 227
    UNIX_SPRING = 228
    UNIX_FALL = 229
    UNIX_WINTER = 230
    UNIX_SUMMER = 231

    # Lilian date, number of days elapsed since the beginning of
    # the Gregorian Calendar on 15 October 1582.
    LILIAN_MICROSECOND = 232
    LILIAN_MILLISECOND = 233
    LILIAN_SECOND = 234
    LILIAN_MINUTE = 235
    LILIAN_HOUR = 236
    LILIAN_DAY = 237
    LILIAN_WEEK = 238
    LILIAN_WEEKEND = 239
    LILIAN_MONTH = 240
    LILIAN_YEAR = 241
    LILIAN_DECADE = 242
    LILIAN_CENTURY = 243
    LILIAN_MILLENNIUM = 244

    LILIAN_SEASON = 245
    LILIAN_SPRING = 246
    LILIAN_FALL = 247
    LILIAN_WINTER = 248
    LILIAN_SUMMER = 249

    # Rata Die, number of days elapsed since 1 January 1 AD 1 in the
    # proleptic Gregorian calendar. Equivalent to absolute units
    RATADIE_MICROSECOND = 250
    RATADIE_MILLISECOND = 251
    RATADIE_SECOND = 252
    RATADIE_MINUTE = 253
    RATADIE_HOUR = 254
    RATADIE_DAY = 255
    RATADIE_WEEK = 256
    RATADIE_WEEKEND = 257
    RATADIE_MONTH = 258
    RATADIE_YEAR = 259
    RATADIE_DECADE = 260
    RATADIE_CENTURY = 261
    RATADIE_MILLENNIUM = 262

    RATADIE_SEASON = 263
    RATADIE_SPRING = 264
    RATADIE_FALL = 265
    RATADIE_WINTER = 266
    RATADIE_SUMMER = 267


class Season(Enum):
    SPRING = 0
    SUMMER = 1
    FALL = 2
    WINTER = 3
