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
import unittest
from datetime import datetime, timedelta

from lingua_franca import set_default_lang, \
    load_language, unload_language
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.time import default_timezone


def setUpModule():
    load_language("ru-ru")
    set_default_lang("ru")


def tearDownModule():
    unload_language("ru")


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("ты и мы", "ты и мы") >= 1.0)
        self.assertTrue(fuzzy_match("ты и мы", "ты") < 0.5)
        self.assertTrue(fuzzy_match("Ты", "ты") >= 0.5)
        self.assertTrue(fuzzy_match("ты и мы", "ты") ==
                        fuzzy_match("ты", "ты и мы"))
        self.assertTrue(fuzzy_match("ты и мы", "он или они") < 0.36)

    def test_match_one(self):
        # test list of choices
        choices = ['фрэнк', 'кейт', 'гарри', 'генри']
        self.assertEqual(match_one('фрэнк', choices)[0], 'фрэнк')
        self.assertEqual(match_one('фрэн', choices)[0], 'фрэнк')
        self.assertEqual(match_one('енри', choices)[0], 'генри')
        self.assertEqual(match_one('кэтт', choices)[0], 'кейт')
        # test dictionary of choices
        choices = {'фрэнк': 1, 'кейт': 2, 'гарри': 3, 'генри': 4}
        self.assertEqual(match_one('фрэнк', choices)[0], 1)
        self.assertEqual(match_one('енри', choices)[0], 4)


class TestNormalize(unittest.TestCase):

    def test_extract_number(self):
        self.assertEqual(extract_number("это первый тест",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("это 2 тест"), 2)
        self.assertEqual(extract_number("это второй тест",
                                        ordinals=True), 2)
        # self.assertEqual(extract_number("этот один третий тест"), 1.0 / 3.0)
        self.assertEqual(extract_number("этот один третий тест",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("это четвёртый", ordinals=True), 4.0)
        self.assertEqual(extract_number(
            "это тридцать шестой", ordinals=True), 36.0)
        self.assertEqual(extract_number("это тест на число 4"), 4)
        self.assertEqual(extract_number("одна треть чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("три чашки"), 3)
        self.assertEqual(extract_number("1/3 чашки"), 1.0 / 3.0)
        self.assertEqual(extract_number("четверть чашки"), 0.25)
        self.assertEqual(extract_number("одна четвёртая чашки"), 0.25)
        self.assertEqual(extract_number("1/4 чашки"), 0.25)
        self.assertEqual(extract_number("2/3 чашки"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 и 3/4 чашки"), 1.75)
        self.assertEqual(extract_number("1 чашка с половиной"), 1.5)
        self.assertEqual(extract_number("один чашка с половиной"), 1.5)
        self.assertEqual(extract_number("одна и половина чашки"), 1.5)
        self.assertEqual(extract_number("одна с половиной чашка"), 1.5)
        self.assertEqual(extract_number("одна и одна половина чашки"), 1.5)
        # self.assertEqual(extract_number("три четверти чашки"), 3.0 / 4.0)
        # self.assertEqual(extract_number("три четвёртые чашки"), 3.0 / 4.0)
        self.assertEqual(extract_number("двадцать два"), 22)
        self.assertEqual(extract_number(
            "Двадцать два с заглавной буквой в начале"), 22)
        self.assertEqual(extract_number(
            "Двадцать Два с двумя заглавными буквами"), 22)
        self.assertEqual(extract_number(
            "двадцать Два с другой заглавной буквой"), 22)
        # self.assertEqual(extract_number("Двадцать два и Три Пятых"), 22.6)
        self.assertEqual(extract_number("двести"), 200)
        self.assertEqual(extract_number("девять тысяч"), 9000)
        self.assertEqual(extract_number("шестьсот шестьдесят шесть"), 666)
        self.assertEqual(extract_number("два миллиона"), 2000000)
        self.assertEqual(extract_number("два миллиона пятьсот тысяч "
                                        "тонн чугуна"), 2500000)
        self.assertEqual(extract_number("шесть триллионов"), 6000000000000.0)
        self.assertEqual(extract_number("шесть триллионов", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("один точка пять"), 1.5)
        self.assertEqual(extract_number("три точка четырнадцать"), 3.14)
        self.assertEqual(extract_number("ноль точка два"), 0.2)
        self.assertEqual(extract_number("миллиард лет"),
                         1000000000.0)
        self.assertEqual(extract_number("биллион лет",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("сто тысяч"), 100000)
        self.assertEqual(extract_number("минус 2"), -2)
        self.assertEqual(extract_number("минус семьдесят"), -70)
        self.assertEqual(extract_number("тысяча миллионов"), 1000000000)
        self.assertEqual(extract_number("миллиард", short_scale=False),
                         1000000000)
        # self.assertEqual(extract_number("шестая треть"),
        #                  1 / 6 / 3)
        # self.assertEqual(extract_number("шестая треть", ordinals=True),
        #                  6)
        self.assertEqual(extract_number("тридцать секунд"), 30)
        self.assertEqual(extract_number("тридцать два", ordinals=True), 32)
        self.assertEqual(extract_number("вот это миллиардный тест",
                                        ordinals=True), 1e09)
        self.assertEqual(extract_number("вот это одна миллиардная теста"), 1e-9)
        self.assertEqual(extract_number("вот это биллионный тест",
                                        ordinals=True,
                                        short_scale=False), 1e12)
        # self.assertEqual(extract_number("вот это одна биллионная теста",
        #                                 short_scale=False), 1e-12)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("двадцать тысяч"), 20000)
        self.assertEqual(extract_number("пятьдесят миллионов"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("двадцать миллиардов триста миллионов "
                                        "девятьсот пятьдесят тысяч "
                                        "шестьсот семьдесят пять точка восемь"),
                         20300950675.8)
        self.assertEqual(extract_number("девятьсот девяносто девять миллионов "
                                        "девятьсот девяносто девять тысяч "
                                        "девятьсот девяносто девять точка девять"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("восемьсот триллионов двести \
                                        пятьдесят семь"), 800000000000257.0)

        # TODO handle this case
        # self.assertEqual(
        #    extract_number("6 dot six six six"),
        #    6.666)
        self.assertTrue(extract_number("Теннисист скорый") is False)
        self.assertTrue(extract_number("хрупкий") is False)

        self.assertTrue(extract_number("хрупкий ноль") is not False)
        self.assertEqual(extract_number("хрупкий ноль"), 0)

        self.assertTrue(extract_number("грубый 0") is not False)
        self.assertEqual(extract_number("грубый 0"), 0)

        self.assertEqual(extract_number("пара пива"), 2)
        # self.assertEqual(extract_number("пара сотен пив"), 200)
        self.assertEqual(extract_number("пара тысяч пив"), 2000)

        self.assertEqual(extract_number(
            "вот это 7 тест", ordinals=True), 7)
        self.assertEqual(extract_number(
            "вот это 7 тест", ordinals=False), 7)
        self.assertTrue(extract_number("вот это n. тест") is False)
        self.assertEqual(extract_number("вот это 1. тест"), 1)
        self.assertEqual(extract_number("вот это 2. тест"), 2)
        self.assertEqual(extract_number("вот это 3. тест"), 3)
        self.assertEqual(extract_number("вот это 31. тест"), 31)
        self.assertEqual(extract_number("вот это 32. тест"), 32)
        self.assertEqual(extract_number("вот это 33. тест"), 33)
        self.assertEqual(extract_number("вот это 34. тест"), 34)
        self.assertEqual(extract_number("в общем 100%"), 100)

    def test_extract_duration_ru(self):
        self.assertEqual(extract_duration("10 секунд"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 минут"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 часа"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 дня"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 недель"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("семь часов"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 секунд"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("восемь с половиной дней "
                                          "тридцать девять секунд"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("Установи таймер на 30 минут"),
                         (timedelta(minutes=30), "установи таймер на"))
        self.assertEqual(extract_duration("Четыре с половиной минуты до"
                                          " заката"),
                         (timedelta(minutes=4.5), "до заката"))
        self.assertEqual(extract_duration("девятнадцать минут через час"),
                         (timedelta(minutes=19), "через час"))
        # self.assertEqual(extract_duration("разбуди меня через три недели, "
        #                                   "четыреста девяносто семь дней "
        #                                   "и триста 91.6 секунд"),
        #                  (timedelta(weeks=3, days=497, seconds=391.6),
        #                   "разбуди меня через , a"))
        self.assertEqual(extract_duration("фильм один час пятьдесят семь"
                                          " и пол минуты длиной"),
                         (timedelta(hours=1, minutes=57.5),
                          "фильм   длиной"))
        self.assertEqual(extract_duration("10-секунд"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-минут"),
                         (timedelta(minutes=5), ""))

    def test_extractdatetime_ru(self):
        def extractWithFormat(text):
            # Tue June 27, 2017 @ 1:04pm
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("теперь пора",
                    "2017-06-27 13:04:00", "пора")
        self.u = "секунду"
        testExtract("через %s" % self.u,
                    "2017-06-27 13:04:01", "")
        testExtract("через минуту",
                    "2017-06-27 13:05:00", "")
        testExtract("через две минуты",
                    "2017-06-27 13:06:00", "")
        # testExtract("через пару минут",
        #            "2017-06-27 13:06:00", "")
        testExtract("через два часа",
                    "2017-06-27 15:04:00", "")
        # testExtract("через пару часов",
        #            "2017-06-27 15:04:00", "")
        testExtract("через две недели",
                   "2017-07-11 00:00:00", "")
        # testExtract("через пару недель",
        #            "2017-07-11 00:00:00", "")
        testExtract("через два месяца",
                    "2017-08-27 00:00:00", "")
        testExtract("через два года",
                    "2019-06-27 00:00:00", "")
        # testExtract("через пару месяцев",
        #            "2017-08-27 00:00:00", "")
        # testExtract("через пару лет",
        #            "2019-06-27 00:00:00", "")
        testExtract("через десятилетие",
                    "2027-06-27 00:00:00", "")
        # testExtract("через пару десятилетий",
        #            "2037-06-27 00:00:00", "")
        testExtract("следующее десятилетие",
                    "2027-06-27 00:00:00", "")
        testExtract("через столетие",
                    "2117-06-27 00:00:00", "")
        testExtract("через тысячелетие",
                    "3017-06-27 00:00:00", "")
        # testExtract("через два десятилетия",
        #             "2037-06-27 00:00:00", "")
        # testExtract("через 5 десятилетий",
        #             "2067-06-27 00:00:00", "")
        # testExtract("через два века",
        #             "2217-06-27 00:00:00", "")
        # testExtract("через пару веков",
        #            "2217-06-27 00:00:00", "")
        # testExtract("через два тысячелетия",
        #             "4017-06-27 00:00:00", "")
        # testExtract("через две тысячи лет",
        #             "4017-06-27 00:00:00", "")
        # testExtract("через пару тысячелетий",
        #            "4017-06-27 00:00:00", "")
        # testExtract("через пару тысяч лет",
        #            "4017-06-27 00:00:00", "")
        testExtract("через год",
                    "2018-06-27 00:00:00", "")
        testExtract("хочу мороженое через час",
                    "2017-06-27 14:04:00", "хочу мороженое")
        testExtract("через 1 секунду",
                    "2017-06-27 13:04:01", "")
        testExtract("через 2 секунды",
                    "2017-06-27 13:04:02", "")
        testExtract("Установи таймер на 1 минуту",
                    "2017-06-27 13:05:00", "установи таймер")
        testExtract("Установи таймер на пол часа",
                    "2017-06-27 13:34:00", "установи таймер")
        # testExtract("Установи таймер на 5 дней с сегодня",
        #             "2017-07-02 00:00:00", "установи таймер")
        testExtract("послезавтра",
                    "2017-06-29 00:00:00", "")
        testExtract("после завтра",
                    "2017-06-29 00:00:00", "")
        testExtract("Какая погода послезавтра?",
                    "2017-06-29 00:00:00", "какая погода")
        testExtract("Напомни мне в 10:45 pm",
                    "2017-06-27 22:45:00", "напомни мне")
        testExtract("Напомни мне в 10:45 вечера",
                    "2017-06-27 22:45:00", "напомни мне")
        testExtract("какая погода в пятницу утром",
                    "2017-06-30 08:00:00", "какая погода")
        testExtract("какая завтра погода",
                    "2017-06-28 00:00:00", "какая погода")
        testExtract("какая погода сегодня днём",
                    "2017-06-27 15:00:00", "какая погода")
        testExtract("какая погода сегодня вечером",
                    "2017-06-27 19:00:00", "какая погода")
        testExtract("какая была погода сегодня утром",
                    "2017-06-27 08:00:00", "какая была погода")
        testExtract("напомни мне позвонить маме через 8 недель и 2 дня",
                    "2017-08-24 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в августе 3",
                    "2017-08-03 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 7am",
                    "2017-06-28 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 7утра",
                    "2017-06-28 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 10pm",
                    "2017-06-28 22:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 7 вечера",
                    "2017-06-28 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 10 вечера",
                    "2017-06-28 22:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 7 часов вечера",
                    "2017-06-28 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне завтра позвонить маме в 10 часов вечера",
                    "2017-06-28 22:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7am",
                    "2017-06-28 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7утра",
                    "2017-06-28 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через час",
                    "2017-06-27 14:04:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 1730",
                    "2017-06-27 17:30:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 0630",
                    "2017-06-28 06:30:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 06 30 часов",
                    "2017-06-28 06:30:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 06 30",
                    "2017-06-28 06:30:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 06 30 часа",
                    "2017-06-28 06:30:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7 часов",
                    "2017-06-27 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме вечером в 7 часов",
                    "2017-06-27 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме  в 7 часов вечером",
                    "2017-06-27 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7 часов утра",
                    "2017-06-28 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в четверг вечером в 7 часов",
                    "2017-06-29 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в четверг утром в 7 часов",
                    "2017-06-29 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7 часов в четверг утром",
                    "2017-06-29 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7:00 в четверг утром",
                    "2017-06-29 07:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 7:00 в четверг вечером",
                    "2017-06-29 19:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 8 вечера среды",
                    "2017-06-28 20:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 8 в среду вечером",
                    "2017-06-28 20:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме вечером среды в 8",
                    "2017-06-28 20:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через два часа",
                    "2017-06-27 15:04:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 2 часа",
                    "2017-06-27 15:04:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 15 минут",
                    "2017-06-27 13:19:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через пятнадцать минут",
                    "2017-06-27 13:19:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через пол часа",
                    "2017-06-27 13:34:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через четверть часа",
                    "2017-06-27 13:19:00", "напомни мне позвонить маме")
        # testExtract("напомни мне позвонить маме в 10am на 2 день после этой субботы",
        #             "2017-07-03 10:00:00", "напомни мне позвонить маме")
        testExtract("Слушайте музыку Рика Эстли через 2 дня с пятницы",
                    "2017-07-02 00:00:00", "слушайте музыку рика эстли")
        testExtract("Начать вторжение в 3:45 pm в четверг",
                    "2017-06-29 15:45:00", "начать вторжение")
        testExtract("Начать вторжение в 3:45 вечера в четверг",
                    "2017-06-29 15:45:00", "начать вторжение")
        testExtract("Начать вторжение в 3:45 дня в четверг",
                    "2017-06-29 15:45:00", "начать вторжение")
        testExtract("В понедельник закажи торт из пекарни",
                    "2017-07-03 00:00:00", "закажи торт из пекарни")
        testExtract("Включи музыку с днем рождения через 5 лет",
                    "2022-06-27 00:00:00", "включи музыку с днем рождения")
        testExtract("Скайп Маме в 12:45 pm в следующий четверг",
                    "2017-07-06 12:45:00", "скайп маме")
        testExtract("Скайп Маме в 12:45 дня в следующий четверг",
                    "2017-07-06 12:45:00", "скайп маме")
        testExtract("Какая погода в следующую пятницу?",
                    "2017-06-30 00:00:00", "какая погода")
        testExtract("Какая погода в следующую среду?",
                    "2017-07-05 00:00:00", "какая погода")
        testExtract("Какая погода в следующий четверг?",
                    "2017-07-06 00:00:00", "какая погода")
        testExtract("Какая погода в следующую пятницу утром",
                    "2017-06-30 08:00:00", "какая погода")
        testExtract("какая погода в следующую пятницу вечером",
                    "2017-06-30 19:00:00", "какая погода")
        testExtract("какая погода в следующую пятницу днём",
                    "2017-06-30 15:00:00", "какая погода")
        testExtract("какая погода в следующую пятницу в полдень",
                    "2017-06-30 12:00:00", "какая погода")
        testExtract("напомни мне позвонить маме третьего августа",
                    "2017-08-03 00:00:00", "напомни мне позвонить маме")
        # testExtract("купить фейерверк в 4 в четверг",
        #             "2017-07-04 00:00:00", "купить фейерверк")
        testExtract("какая погода через 2 недели со следующей пятницы",
                    "2017-07-14 00:00:00", "какая погода")
        testExtract("какая погода в среду в 0700 часов",
                    "2017-06-28 07:00:00", "какая погода")
        testExtract("Поставь будильник в среду в 7 часов",
                    "2017-06-28 07:00:00", "поставь будильник")
        testExtract("Назначь встречу в 12:45 pm в следующий четверг",
                    "2017-07-06 12:45:00", "назначь встречу")
        testExtract("Назначь встречу в 12:45 дня в следующий четверг",
                    "2017-07-06 12:45:00", "назначь встречу")
        testExtract("Какая погода в этот четверг?",
                    "2017-06-29 00:00:00", "какая погода")
        testExtract("назначь встречу через 2 недели и 6 дней с субботы",
                    "2017-07-21 00:00:00", "назначь встречу")
        testExtract("Начать вторжение в 03 45 в четверг",
                    "2017-06-29 03:45:00", "начать вторжение")
        testExtract("Начать вторжение в 800 часов в четверг",
                    "2017-06-29 08:00:00", "начать вторжение")
        testExtract("Начать вечеринку в 8 часов вечером в четверг",
                    "2017-06-29 20:00:00", "начать вечеринку")
        testExtract("Начать вторжение в 8 вечера в четверг",
                    "2017-06-29 20:00:00", "начать вторжение")
        testExtract("Начать вторжение в четверг в полдень",
                    "2017-06-29 12:00:00", "начать вторжение")
        testExtract("Начать вторжение в четверг в полночь",
                    "2017-06-29 00:00:00", "начать вторжение")
        testExtract("Начать вторжение в четверг в 0500",
                    "2017-06-29 05:00:00", "начать вторжение")
        testExtract("напомни мне встать через 4 года",
                    "2021-06-27 00:00:00", "напомни мне встать")
        testExtract("напомни мне встать через 4 года и 4 дня",
                    "2021-07-01 00:00:00", "напомни мне встать")
        # testExtract("какая погода 3 дня после завтра?",
        #             "2017-07-01 00:00:00", "какая погода")
        testExtract("3 декабря",
                    "2017-12-03 00:00:00", "")
        testExtract("мы встретимся в 8:00 сегодня вечером",
                    "2017-06-27 20:00:00", "мы встретимся")
        testExtract("мы встретимся в 5pm",
                    "2017-06-27 17:00:00", "мы встретимся")
        testExtract("мы встретимся в 5дня",
                    "2017-06-27 17:00:00", "мы встретимся")
        testExtract("мы встретимся в 8 am",
                    "2017-06-28 08:00:00", "мы встретимся")
        testExtract("мы встретимся в 8 утра",
                    "2017-06-28 08:00:00", "мы встретимся")
        testExtract("мы встретимся в 8 вечера",
                    "2017-06-27 20:00:00", "мы встретимся")
        testExtract("напомнить мне встать в 8 am",
                    "2017-06-28 08:00:00", "напомнить мне встать")
        testExtract("напомнить мне встать в 8 утра",
                    "2017-06-28 08:00:00", "напомнить мне встать")
        testExtract("какая погода во вторник",
                    "2017-06-27 00:00:00", "какая погода")
        testExtract("какая погода в понедельник",
                    "2017-07-03 00:00:00", "какая погода")
        testExtract("какая погода в эту среду",
                    "2017-06-28 00:00:00", "какая погода")
        testExtract("в четверг какая погода",
                    "2017-06-29 00:00:00", "какая погода")
        testExtract("в этот четверг какая погода",
                    "2017-06-29 00:00:00", "какая погода")
        testExtract("в прошлый понедельник какая была погода",
                    "2017-06-26 00:00:00", "какая была погода")
        testExtract("поставь будильник на среду вечером в 8",
                    "2017-06-28 20:00:00", "поставь будильник")
        testExtract("поставь будильник на среду в 3 часа дня",
                    "2017-06-28 15:00:00", "поставь будильник")
        testExtract("поставь будильник на среду в 3 часа утра",
                    "2017-06-28 03:00:00", "поставь будильник")
        testExtract("поставь будильник на среду утром в 7 часов",
                    "2017-06-28 07:00:00", "поставь будильник")
        testExtract("поставь будильник на сегодня в 7 часов",
                    "2017-06-27 19:00:00", "поставь будильник")
        testExtract("поставь будильник на этот вечер в 7 часов",
                    "2017-06-27 19:00:00", "поставь будильник")
        testExtract("поставь будильник на этот вечер в 7:00",
                    "2017-06-27 19:00:00", "поставь будильник")
        # testExtract("поставь будильник этим вечером в 7:00",
        #             "2017-06-27 19:00:00", "поставь будильник")
        testExtract("вечером 5 июня 2017 напомни мне позвонить маме",
                    "2017-06-05 19:00:00", "напомни мне позвонить маме")
        testExtract("обнови мой календарь утром свидание с юлиусом" +
                    " 4 марта",
                    "2018-03-04 08:00:00",
                    "обнови мой календарь свидание с юлиусом")
        testExtract("напомни мне позвонить маме в следующий вторник",
                    "2017-07-04 00:00:00", "напомни мне позвонить маме")
        # testExtract("напомни мне позвонить маме  3 недели",
        #             "2017-07-18 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 8 недель",
                    "2017-08-22 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 8 недель и 2 дня",
                    "2017-08-24 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 4 дня",
                    "2017-07-01 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 3 месяца",
                    "2017-09-27 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме через 2 года и 2 дня",
                    "2019-06-29 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме на следующей неделе",
                    "2017-07-04 00:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 10am в субботу",
                    "2017-07-01 10:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 10 утра в субботу",
                    "2017-07-01 10:00:00", "напомни мне позвонить маме")
        # testExtract("напомни мне позвонить маме в 10am в эту субботу",
        #             "2017-07-01 10:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 10 в следующую субботу",
                    "2017-07-01 10:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 10am в следующую субботу",
                    "2017-07-01 10:00:00", "напомни мне позвонить маме")
        testExtract("напомни мне позвонить маме в 10 утра в следующую субботу",
                    "2017-07-01 10:00:00", "напомни мне позвонить маме")
        # test yesterday
        testExtract("какой был день вчера",
                    "2017-06-26 00:00:00", "какой был день")
        testExtract("какой был день позавчера",
                    "2017-06-25 00:00:00", "какой был день")
        testExtract("я позавтракал вчера в 6",
                    "2017-06-26 06:00:00", "я позавтракал")
        testExtract("я позавтракал вчера в 6 am",
                    "2017-06-26 06:00:00", "я позавтракал")
        testExtract("я позавтракал вчера в 6 утра",
                    "2017-06-26 06:00:00", "я позавтракал")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight

        testExtract("поставь будильник на 9 в выходные",
                    "2017-06-27 21:00:00", "поставь будильник выходные")
        testExtract("на 8 сегодня вечером",
                    "2017-06-27 20:00:00", "")
        testExtract("на 8:30pm сегодня вечером",
                    "2017-06-27 20:30:00", "")
        testExtract("на 8:30вечера сегодня",
                    "2017-06-27 20:30:00", "")
        testExtract("на 8:30 вечера сегодня",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("поставь будильник сегодня вечером на 9:30",
                    "2017-06-27 21:30:00", "поставь будильник")
        testExtract("поставь будильник на 9:00 сегодня вечером",
                    "2017-06-27 21:00:00", "поставь будильник")
        # Check if it picks intent irrespective of correctness
        testExtract("поставь будильник в 9 часов сегодня вечером",
                    "2017-06-27 21:00:00", "поставь будильник")
        testExtract("напомни мне об игре сегодня вечером в 11:30",
                    "2017-06-27 23:30:00", "напомни мне об игре")
        testExtract("поставь будильник в 7:30 на выходных",
                    "2017-06-27 19:30:00", "поставь будильник на выходных")

        #  "# days <from X/after X>"
        testExtract("мой день рождения через 2 дня с сегодня",
                    "2017-06-29 00:00:00", "мой день рождения")
        testExtract("мой день рождения через 2 дня от сегодня",
                    "2017-06-29 00:00:00", "мой день рождения")
        testExtract("мой день рождения через 2 дня с завтра",
                    "2017-06-30 00:00:00", "мой день рождения")
        testExtract("мой день рождения через 2 дня от завтра",
                    "2017-06-30 00:00:00", "мой день рождения")
        # testExtract("напомни мне позвонить маме в 10am через 2 дня после следующей субботы",
        #             "2017-07-10 10:00:00", "напомни мне позвонить маме")
        testExtract("мой день рождения через 2 дня со вчера",
                    "2017-06-28 00:00:00", "мой день рождения")
        testExtract("мой день рождения через 2 дня от вчера",
                    "2017-06-28 00:00:00", "мой день рождения")

        #  "# days ago>"
        testExtract("мой день рождения был 1 день назад",
                    "2017-06-26 00:00:00", "мой день рождения был")
        testExtract("мой день рождения был 2 дня назад",
                    "2017-06-25 00:00:00", "мой день рождения был")
        testExtract("мой день рождения был 3 дня назад",
                    "2017-06-24 00:00:00", "мой день рождения был")
        testExtract("мой день рождения был 4 дня назад",
                    "2017-06-23 00:00:00", "мой день рождения был")
        testExtract("мой день рождения был 5 дней назад",
                    "2017-06-22 00:00:00", "мой день рождения был")
        testExtract("встретимся сегодня ночью",
                    "2017-06-27 22:00:00", "встретимся ночью")
        testExtract("встретимся позже ночью",
                    "2017-06-27 22:00:00", "встретимся позже ночью")
        testExtract("какая будет погода завтра ночью",
                    "2017-06-28 22:00:00", "какая будет погода ночью")
        testExtract("какая будет погода в следующий вторник ночью",
                    "2017-07-04 22:00:00", "какая будет погода ночью")

    def test_extract_ambiguous_time_ru(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        evening = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(extract_datetime('кормление рыб'), None)
        self.assertEqual(extract_datetime('день'), None)
        # self.assertEqual(extract_datetime('сегодня'), None)
        self.assertEqual(extract_datetime('месяц'), None)
        self.assertEqual(extract_datetime('год'), None)
        self.assertEqual(extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('покормить рыб в 10 часов', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('покормить рыб в 10 часов', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('покормить рыб в 10 часов', evening)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    def test_extract_relativedatetime_ru(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("мы встретимся через 5 минут",
                    "2017-06-27 10:06:02", "мы встретимся")
        # testExtract("мы встретимся через 5минут",
        #             "2017-06-27 10:06:02", "мы встретимся")
        testExtract("мы встретимся через 5 секунд",
                    "2017-06-27 10:01:07", "мы встретимся")
        testExtract("мы встретимся через 1 час",
                    "2017-06-27 11:01:02", "мы встретимся")
        testExtract("мы встретимся через 2 часа",
                    "2017-06-27 12:01:02", "мы встретимся")
        testExtract("мы встретимся через 1 минуту",
                    "2017-06-27 10:02:02", "мы встретимся")
        testExtract("мы встретимся через 1 секунду",
                    "2017-06-27 10:01:03", "мы встретимся")
        # testExtract("мы встретимся через 5секунд",
        #             "2017-06-27 10:01:07", "мы встретимся")

    def test_spaces(self):
        self.assertEqual(normalize("  вот   это   тест"),
                         "вот это тест")
        self.assertEqual(normalize("  вот   это     тест  "),
                         "вот это тест")
        self.assertEqual(normalize("  вот   это  один    тест"),
                         "вот это 1 тест")

    def test_numbers(self):
        self.assertEqual(normalize("вот это один два три  тест"),
                         "вот это 1 2 3 тест")
        self.assertEqual(normalize("  вот это четыре пять шесть  тест"),
                         "вот это 4 5 6 тест")
        self.assertEqual(normalize("вот это семь восемь девять тест"),
                         "вот это 7 8 9 тест")
        self.assertEqual(normalize("вот это семь восемь девять  тест"),
                         "вот это 7 8 9 тест")
        self.assertEqual(normalize("вот это десять одиннадцать двенадцать тест"),
                         "вот это 10 11 12 тест")
        self.assertEqual(normalize("вот это тринадцать четырнадцать тест"),
                         "вот это 13 14 тест")
        self.assertEqual(normalize("вот это пятнадцать шестнадцать семнадцать"),
                         "вот это 15 16 17")
        self.assertEqual(normalize("вот это восемнадцать девятнадцать двадцать"),
                         "вот это 18 19 20")
        self.assertEqual(normalize("вот это один девятнадцать двадцать два"),
                         "вот это 1 19 20 2")
        self.assertEqual(normalize("вот это один сто"),
                         "вот это 1 сто")
        self.assertEqual(normalize("вот это один два двадцать два"),
                         "вот это 1 2 20 2")
        self.assertEqual(normalize("вот это один и половина"),
                         "вот это 1 и половина")
        self.assertEqual(normalize("вот это один и половина и пять шесть"),
                         "вот это 1 и половина и 5 6")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("вот это один два три тест"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("вот это четыре пять шесть тест"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("вот это десять одиннадцать двенадцать тест"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("вот это один двадцать один тест"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 собака, семь свиней, у макдонадьда "
                                         "была ферма ферма, 3 раза по 5 макарен"),
                         [1, 7, 3, 5])
        # self.assertEqual(extract_numbers("два пива для двух медведей"),
        #                  [2.0, 2.0])
        self.assertEqual(extract_numbers("двадцать 20 двадцать"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("двадцать 20 22"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("двадцать двадцать два двадцать"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("двадцать 2"),
                         [22.0])
        self.assertEqual(extract_numbers("двадцать 20 двадцать 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("треть один"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("третий", ordinals=True), [3])
        self.assertEqual(extract_numbers("шесть триллионов", short_scale=True),
                         [6e12])
        self.assertEqual(extract_numbers("шесть триллионов", short_scale=False),
                         [6e18])
        self.assertEqual(extract_numbers("два поросёнка и шесть триллионов бактерий",
                                         short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("два поросёнка и шесть триллионов бактерий",
                                         short_scale=False), [2, 6e18])
        self.assertEqual(extract_numbers("тридцать второй или первый",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("вот это семь восемь девять и"
                                         " половина тест"),
                         [7.0, 8.0, 9.5])


if __name__ == "__main__":
    unittest.main()
