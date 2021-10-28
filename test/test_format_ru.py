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
import unittest
import datetime
import ast
import sys
from pathlib import Path

from lingua_franca import get_default_lang, set_default_lang, \
    load_language, unload_language
from lingua_franca.format import date_time_format
from lingua_franca.format import join_list
from lingua_franca.format import nice_date
from lingua_franca.format import nice_date_time
from lingua_franca.format import nice_duration
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import nice_year
from lingua_franca.format import pronounce_number
from lingua_franca.time import default_timezone


def setUpModule():
    load_language("ru-ru")
    set_default_lang("ru")


def tearDownModule():
    unload_language("ru")


NUMBERS_FIXTURE_RU = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: 'половина',
    1.333: '1 и 1 треть',
    2.666: '2 и 2 трети',
    0.25: 'четверть',
    1.25: '1 и 1 четверть',
    0.75: '3 четверти',
    1.75: '1 и 3 четверти',
    3.4: '3 и 2 пятые',
    16.8333: '16 и 5 шестых',
    12.5714: '12 и 4 седьмые',
    9.625: '9 и 5 восьмых',
    6.777: '6 и 7 девятых',
    3.1: '3 и 1 десятая',
    2.272: '2 и 3 одиннадцатые',
    5.583: '5 и 7 двенадцатых',
    8.384: '8 и 5 тринадцатых',
    0.071: '1 четырнадцатая',
    6.466: '6 и 7 пятнадцатых',
    8.312: '8 и 5 шестнадцатых',
    2.176: '2 и 3 семнадцатые',
    200.722: '200 и 13 восемнадцатых',
    7.421: '7 и 8 девятнадцатых',
    0.05: '1 двадцатая'
}


class TestNiceNumberFormat(unittest.TestCase):

    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_RU.items():
            self.assertEqual(nice_number(number, speech=True), number_str,
                             'должен отформатировать {} как {}, а не {}'.format(
                                 number, number_str, nice_number(number, speech=True)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, speech=True, denominators=[1, 2, 3]),
                         '5 с половиной',
                         'должен отформатировать 5.5 как 5 с половиной, а не {}'.format(
                             nice_number(5.5, speech=True, denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, speech=True, denominators=[1, 2]),
                         '2.333',
                         'должен отформатировать 2.333 как 2.333, а не {}'.format(
                             nice_number(2.333, speech=True, denominators=[1, 2])))

    def test_no_speech(self):
        self.assertEqual(nice_number(6.777, speech=False),
                         '6 7/9',
                         'должен отформатировать 6.777 как 6 7/9, а не {}'.format(
                             nice_number(6.777, speech=False)))
        self.assertEqual(nice_number(6.0, speech=False),
                         '6',
                         'должен отформатировать 6.0 как 6, а не {}'.format(
                             nice_number(6.0, speech=False)))


class TestPronounceNumber(unittest.TestCase):

    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "ноль")
        self.assertEqual(pronounce_number(1), "один")
        self.assertEqual(pronounce_number(10), "десять")
        self.assertEqual(pronounce_number(15), "пятнадцать")
        self.assertEqual(pronounce_number(20), "двадцать")
        self.assertEqual(pronounce_number(27), "двадцать семь")
        self.assertEqual(pronounce_number(30), "тридцать")
        self.assertEqual(pronounce_number(33), "тридцать три")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "минус один")
        self.assertEqual(pronounce_number(-10), "минус десять")
        self.assertEqual(pronounce_number(-15), "минус пятнадцать")
        self.assertEqual(pronounce_number(-20), "минус двадцать")
        self.assertEqual(pronounce_number(-27), "минус двадцать семь")
        self.assertEqual(pronounce_number(-30), "минус тридцать")
        self.assertEqual(pronounce_number(-33), "минус тридцать три")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "ноль точка ноль пять")
        self.assertEqual(pronounce_number(-0.05), "минус ноль точка ноль пять")
        self.assertEqual(pronounce_number(1.234),
                         "один точка два три")
        self.assertEqual(pronounce_number(21.234),
                         "двадцать один точка два три")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "двадцать один точка два")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "двадцать один")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "двадцать один точка два три четыре")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "двадцать один точка два три четыре")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "двадцать один точка два три четыре")
        self.assertEqual(pronounce_number(-1.234),
                         "минус один точка два три")
        self.assertEqual(pronounce_number(-21.234),
                         "минус двадцать один точка два три")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "минус двадцать один точка два")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "минус двадцать один")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "минус двадцать один точка два три четыре")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "минус двадцать один точка два три четыре")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "минус двадцать один точка два три четыре")

    def test_convert_stos(self):
        self.assertEqual(pronounce_number(100), "сто")
        self.assertEqual(pronounce_number(666), "шестьсот шестьдесят шесть")
        self.assertEqual(pronounce_number(1456), "тысяча четыреста пятьдесят шесть")
        self.assertEqual(pronounce_number(103254654), "сто три миллиона "
                                                      "двести пятьдесят "
                                                      "четыре тысячи "
                                                      "шестьсот "
                                                      "пятьдесят четыре")
        self.assertEqual(pronounce_number(1512457), "миллион пятьсот"
                                                    " двенадцать тысяч "
                                                    "четыреста пятьдесят "
                                                    "семь")
        self.assertEqual(pronounce_number(209996), "двести девять "
                                                   "тысяч девятьсот "
                                                   "девяносто шесть")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "ноль")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "три точка три на десять в степени один")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "два точка девять девять на десять в степени восемь")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "два точка девять девять семь девять два пять "
                         "на десять в степени восемь")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "один точка шесть семь два на десять в степени "
                         "минус двадцать семь")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "один точка один на десять в степени "
                                        "минус сто пятьдесят")

    def test_large_numbers(self):
        self.maxDiff = None
        self.assertEqual(
            pronounce_number(299792458, short_scale=True),
            "двести девяносто девять миллионов семьсот "
            "девяносто две тысячи четыреста пятьдесят восемь")
        self.assertEqual(
            pronounce_number(299792458, short_scale=False),
            "двести девяносто девять миллионов семьсот "
            "девяносто две тысячи четыреста пятьдесят восемь")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=True),
            "сто квинтиллионов тридцать четыре квадриллиона "
            "двести девяносто девять миллионов семьсот "
            "девяносто две тысячи четыреста пятьдесят восемь")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=False),
            "сто биллионов тридцать четыре тысячи миллиардов "
            "двести девяносто девять миллионов семьсот "
            "девяносто две тысячи четыреста пятьдесят восемь")
        self.assertEqual(
            pronounce_number(1e10, short_scale=True),
            "десять миллиардов")
        self.assertEqual(
            pronounce_number(1e12, short_scale=True),
            "триллион")
        # TODO maybe beautify this
        self.assertEqual(
            pronounce_number(1000001, short_scale=True),
            "миллион один")
        self.assertEqual(pronounce_number(95505896639631893, short_scale=True),
                         "девяносто пять квадриллионов "
                         "пятьсот пять триллионов "
                         "восемьсот девяносто шесть миллиардов "
                         "шестьсот тридцать девять миллионов "
                         "шестьсот тридцать одна тысяча "
                         "восемьсот девяносто три")
        self.assertEqual(pronounce_number(95505896639631893,
                                          short_scale=False),
                         "девяносто пять тысяч пятьсот пять миллиардов "
                         "восемьсот девяносто шесть тысяч "
                         "шестьсот тридцать девять миллионов "
                         "шестьсот тридцать одна тысяча "
                         "восемьсот девяносто три")
        self.assertEqual(pronounce_number(10e80, places=1),
                         "секснвигинтиллион")
        # TODO floating point rounding issues might happen
        self.assertEqual(pronounce_number(1.9874522571e80, places=9),
                         "сто девяносто восемь квинвигинтиллионов "
                         "семьсот сорок пять кватторвигинтиллионов "
                         "двести двадцать пять тревигинтиллионов "
                         "семьсот девять дуовигинтиллионов "
                         "девятьсот девяносто девять унвигинтиллионов "
                         "девятьсот восемьдесят девять вигинтиллионов "
                         "семьсот тридцать новемдециллионов "
                         "девятьсот девятнадцать октодециллионов "
                         "девятьсот девяносто девять септендециллионов "
                         "девятьсот пятьдесят пять сексдециллионов "
                         "четыреста девяносто восемь квиндециллионов "
                         "двести четырнадцать кваттордециллионов "
                         "восемьсот сорок пять тредециллионов "
                         "четыреста двадцать девять дуодециллионов "
                         "четыреста сорок четыре ундециллиона "
                         "триста тридцать шесть дециллионов "
                         "семьсот двадцать четыре нониллиона "
                         "пятьсот шестьдесят девять октиллионов "
                         "триста семьдесят пять септиллионов "
                         "двести тридцать девять секстиллионов "
                         "шестьсот семьдесят квинтиллионов "
                         "пятьсот семьдесят четыре квадриллиона "
                         "семьсот тридцать девять триллионов "
                         "семьсот сорок восемь миллиардов "
                         "четыреста семьдесят миллионов "
                         "девятьсот пятнадцать тысяч "
                         "семьдесят два")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "бесконечность")
        self.assertEqual(
            pronounce_number(float("inf")),
            "бесконечность")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "минус бесконечность")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "первый")
        self.assertEqual(pronounce_number(10, ordinals=True), "десятый")
        self.assertEqual(pronounce_number(15, ordinals=True), "пятнадцатый")
        self.assertEqual(pronounce_number(20, ordinals=True), "двадцатый")
        self.assertEqual(pronounce_number(27, ordinals=True), "двадцать седьмой")
        self.assertEqual(pronounce_number(30, ordinals=True), "тридцатый")
        self.assertEqual(pronounce_number(33, ordinals=True), "тридцать третий")
        self.assertEqual(pronounce_number(100, ordinals=True), "сотый")
        self.assertEqual(pronounce_number(1000, ordinals=True), "тысячный")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "десятитысячный")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "восемнадцать тысяч шестьсот девяносто первый")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "тысяча пятьсот шестьдесят седьмой")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "один точка шесть семь два на десять в минус "
                         "двадцать седьмой степени")
        self.assertEqual(pronounce_number(1e6, ordinals=True),
                         "миллионный")
        self.assertEqual(pronounce_number(2e6, ordinals=True),
                         "двухмиллионный")
        self.assertEqual(pronounce_number(2e6, ordinals=True, short_scale=False),
                         "двухмиллионный")
        self.assertEqual(pronounce_number(3e6, ordinals=True),
                         "трёхмиллионный")
        self.assertEqual(pronounce_number(4e6, ordinals=True),
                         "четырёхмиллионный")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "восемнадцатимиллионный")
        self.assertEqual(pronounce_number(18e12, ordinals=True,
                                          short_scale=False),
                         "восемнадцатибиллионный")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "восемнадцатитриллионный")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "восемнадцатитриллионный")


class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            if (sub_dir / 'date_time_test.json').exists():
                print("Loading test for " +
                      str(sub_dir / 'date_time_test.json'))
                with (sub_dir / 'date_time_test.json').open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, speech=True, use_24hour=True, use_ampm=False))

        self.assertEqual(nice_time(dt, use_24hour=False),
                         "час двадцать два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "час двадцать два дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:22 дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "тринадцать двадцать два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "тринадцать двадцать два")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "час")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "час дня")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:00 дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "тринадцать ровно")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "тринадцать ровно")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "час ноль два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "час ноль два дня")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False, use_ampm=True),
                         "1:02 дня")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "тринадцать ноль два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "тринадцать ноль два")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "двенадцать ноль два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "двенадцать ноль два ночи")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "12:02 ночи")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "ноль ноль ноль два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ноль ноль ноль два")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "час ноль два")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "час ноль два ночи")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:02 ночи")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "ноль один ноль два")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ноль один ноль два")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "двенадцать с четвертью")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "двенадцать с четвертью дня")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "пять с половиной утра")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "без четверти два")

    def test_nice_date(self):
        lang = "ru-ru"
        i = 1
        while (self.test_config[lang].get('test_nice_date') and
               self.test_config[lang]['test_nice_date'].get(str(i).encode('utf8'))):
            p = self.test_config[lang]['test_nice_date'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5],
                tzinfo=default_timezone())
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is date ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'],
                             nice_date(dt, lang=lang, now=now))
            i = i + 1

        # test all days in a year for all languages,
        # that some output is produced
        # for lang in self.test_config:
        for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3,
                                     tzinfo=default_timezone()) +
                   datetime.timedelta(n) for n in range(368)):
            self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        lang = "ru-ru"
        i = 1
        while (self.test_config[lang].get('test_nice_date_time') and
               self.test_config[lang]['test_nice_date_time'].get(str(i).encode('utf8'))):
            p = self.test_config[lang]['test_nice_date_time'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5])
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is date time ' + p['assertEqual'])
            self.assertEqual(
                p['assertEqual'],
                nice_date_time(
                    dt, lang=lang, now=now,
                    use_24hour=ast.literal_eval(p['use_24hour']),
                    use_ampm=ast.literal_eval(p['use_ampm'])))
            i = i + 1

    def test_nice_year(self):
        lang = "ru-ru"
        i = 1
        while (self.test_config[lang].get('test_nice_year') and
               self.test_config[lang]['test_nice_year'].get(str(i).encode('utf8'))):
            p = self.test_config[lang]['test_nice_year'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            print('Testing for ' + lang + ' that ' + str(dt) +
                  ' is year ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'], nice_year(
                dt, lang=lang, bc=ast.literal_eval(p['bc'])))
            i = i + 1

        # Test all years from 0 to 9999 for all languages,
        # that some output is produced
        print("Test all years in " + lang)
        for i in range(1, 9999):
            dt = datetime.datetime(i, 1, 31, 13, 2, 3,
                                   tzinfo=default_timezone())
            self.assertTrue(len(nice_year(dt, lang=lang)) > 0)
            # Looking through the date sequence can be helpful

    def test_nice_duration(self):

        self.assertEqual(nice_duration(1), "одна секунда")
        self.assertEqual(nice_duration(3), "три секунды")
        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "одна минута одна секунда")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "один час двадцать три минуты двадцать секунд")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "тринадцать часов пятьдесят три минуты двадцать секунд")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "пять дней восемнадцать часов пятьдесят три минуты двадцать секунд")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "и"), "")
        self.assertEqual(join_list([], "и"), "")

        self.assertEqual(join_list(["a"], "и"), "a")
        self.assertEqual(join_list(["a", "b"], "и"), "a и b")
        self.assertEqual(join_list(["a", "b"], "или"), "a или b")

        self.assertEqual(join_list(["a", "b", "c"], "и"), "a, b и c")
        self.assertEqual(join_list(["a", "b", "c"], "или"), "a, b или c")
        self.assertEqual(
            join_list(["a", "b", "c"], "или", ";"), "a; b или c")
        self.assertEqual(
            join_list(["a", "b", "c", "d"], "или"), "a, b, c или d")

        self.assertEqual(join_list([1, "b", 3, "d"], "или"), "1, b, 3 или d")


if __name__ == "__main__":
    unittest.main()
