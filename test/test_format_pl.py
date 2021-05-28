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
import datetime
import sys

from lingua_franca import get_default_lang, set_default_lang, \
    load_language, unload_language
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import nice_duration
from lingua_franca.format import pronounce_number
from lingua_franca.time import default_timezone



def setUpModule():
    load_language("pl-pl")
    set_default_lang("pl")


def tearDownModule():
    unload_language("pl")


NUMBERS_FIXTURE_PL = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: '1 druga',
    1.333: '1 i 1 trzecia',
    2.666: '2 i 2 trzecie',
    0.25: '1 czwarta',
    1.25: '1 i 1 czwarta',
    0.75: '3 czwarte',
    1.75: '1 i 3 czwarte',
    3.4: '3 i 2 piąte',
    16.8333: '16 i 5 szóste',
    12.5714: '12 i 4 siódme',
    9.625: '9 i 5 ósme',
    6.777: '6 i 7 dziewiąte',
    3.1: '3 i 1 dziesiąta',
    2.272: '2 i 3 jedenaste',
    5.583: '5 i 7 dwunaste',
    8.384: '8 i 5 trzynaste',
    0.071: '1 czternasta',
    6.466: '6 i 7 piętnaste',
    8.312: '8 i 5 szesnaste',
    2.176: '2 i 3 siedemnaste',
    200.722: '200 i 13 osiemnaste',
    7.421: '7 i 8 dziewiętnaste',
    0.05: '1 dwudziesta'
}


class TestNiceNumberFormat(unittest.TestCase):
    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_PL.items():
            self.assertEqual(nice_number(number, lang='pl'), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(number)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, denominators=[1, 2, 3]),
                         '5 i 1 druga',
                         'should format 5.5 as 5 and a half not {}'.format(
                             nice_number(5.5, denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, denominators=[1, 2]),
                         '2.333',
                         'should format 2.333 as 2.333 not {}'.format(
                             nice_number(2.333, denominators=[1, 2])))

    def test_no_speech(self):
        self.assertEqual(nice_number(6.777, speech=False),
                         '6 7/9',
                         'should format 6.777 as 6 7/9 not {}'.format(
                             nice_number(6.777, speech=False)))
        self.assertEqual(nice_number(6.0, speech=False),
                         '6',
                         'should format 6.0 as 6 not {}'.format(
                             nice_number(6.0, speech=False)))


class TestPronounceNumber(unittest.TestCase):
    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "zero")
        self.assertEqual(pronounce_number(1), "jeden")
        self.assertEqual(pronounce_number(10), "dziesięć")
        self.assertEqual(pronounce_number(15), "piętnaście")
        self.assertEqual(pronounce_number(20), "dwadzieścia")
        self.assertEqual(pronounce_number(27), "dwadzieścia siedem")
        self.assertEqual(pronounce_number(30), "trzydzieści")
        self.assertEqual(pronounce_number(33), "trzydzieści trzy")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "minus jeden")
        self.assertEqual(pronounce_number(-10), "minus dziesięć")
        self.assertEqual(pronounce_number(-15), "minus piętnaście")
        self.assertEqual(pronounce_number(-20), "minus dwadzieścia")
        self.assertEqual(pronounce_number(-27), "minus dwadzieścia siedem")
        self.assertEqual(pronounce_number(-30), "minus trzydzieści")
        self.assertEqual(pronounce_number(-33), "minus trzydzieści trzy")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "zero przecinek zero pięć")
        self.assertEqual(pronounce_number(-0.05), "minus zero przecinek zero pięć")
        self.assertEqual(pronounce_number(1.234),
                         "jeden przecinek dwa trzy")
        self.assertEqual(pronounce_number(21.234),
                         "dwadzieścia jeden przecinek dwa trzy")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "dwadzieścia jeden przecinek dwa")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "dwadzieścia jeden")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "dwadzieścia jeden przecinek dwa trzy cztery")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "dwadzieścia jeden przecinek dwa trzy cztery")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "dwadzieścia jeden przecinek dwa trzy cztery")
        self.assertEqual(pronounce_number(-1.234),
                         "minus jeden przecinek dwa trzy")
        self.assertEqual(pronounce_number(-21.234),
                         "minus dwadzieścia jeden przecinek dwa trzy")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "minus dwadzieścia jeden przecinek dwa")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "minus dwadzieścia jeden")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "minus dwadzieścia jeden przecinek dwa trzy cztery")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "minus dwadzieścia jeden przecinek dwa trzy cztery")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "minus dwadzieścia jeden przecinek dwa trzy cztery")

    def test_convert_hundreds(self):
        self.assertEqual(pronounce_number(100), "sto")
        self.assertEqual(pronounce_number(666), "sześćset sześćdziesiąt sześć")
        self.assertEqual(pronounce_number(1456), "jeden tysiąc, czterysta pięćdziesiąt sześć")
        self.assertEqual(pronounce_number(103254654), "sto trzy miliony, dwieście "
                                                      "pięćdziesiąt cztery tysiące, sześćset "
                                                      "pięćdziesiąt cztery")
        self.assertEqual(pronounce_number(1512457), "jeden milion, pięćset dwanaście tysięcy, czterysta "
                                                    "pięćdziesiąt siedem")
        self.assertEqual(pronounce_number(209996), "dwieście dziewięć tysięcy, dziewięćset "
                                                   "dziewięćdziesiąt sześć")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "zero")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "trzy przecinek trzy razy dziesięć do potęgi jeden")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "dwa przecinek dziewięć dziewięć razy dziesięć do potęgi osiem")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "dwa przecinek dziewięć dziewięć siedem dziewięć dwa pięć razy "
                         "dziesięć do potęgi osiem")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "jeden przecinek sześć siedem dwa razy dziesięć do potęgi "
                         "minus dwadzieścia siedem")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "jeden przecinek jeden razy dziesięć do "
                                        "potęgi minus sto pięćdziesiąt")

    def test_large_numbers(self):
        self.assertEqual(
            pronounce_number(299792458),
            "dwieście dziewięćdziesiąt dziewięć milionów, siedemset "
            "dziewięćdziesiąt dwa tysiące, czterysta pięćdziesiąt osiem")
        self.assertEqual(
            pronounce_number(100034000000299792458),
            "sto trylionów, trzydzieści cztery biliardy, "
            "dwieście dziewięćdziesiąt dziewięć milionów, siedemset "
            "dziewięćdziesiąt dwa tysiące, czterysta pięćdziesiąt osiem")
        self.assertEqual(
            pronounce_number(10000000000),
            "dziesięć miliardów")
        self.assertEqual(
            pronounce_number(1000001),
            "jeden milion, jeden")
        self.assertEqual(pronounce_number(95505896639631893),
                         "dziewięćdziesiąt pięć biliardów, pięćset pięć "
                         "bilionów, osiemset dziewięćdziesiąt sześć miliardów, "
                         "sześćset trzydzieści dziewięć milionów, sześćset "
                         "trzydzieści jeden tysiące, osiemset dziewięćdziesiąt trzy")
        self.assertEqual(pronounce_number(10e80, places=1),
                         "tredecyliard")
        self.assertEqual(pronounce_number(1.9874522571e80, places=9),
                         "sto dziewięćdziesiąt osiem tredecylionów, "
                         "siedemset czterdzieści pięć duodecyliardów, "
                         "dwieście dwadzieścia pięć duodecylionów, "
                         "siedemset dziewięć undecyliardów, "
                         "dziewięćset dziewięćdziesiąt dziewięć undecylionów, "
                         "dziewięćset osiemdziesiąt dziewięć decyliardów, "
                         "siedemset trzydzieści decylionów, dziewięćset "
                         "dziewiętnaście noniliardów, dziewięćset "
                         "dziewięćdziesiąt dziewięć nonilionów, dziewięćset "
                         "pięćdziesiąt pięć oktyliardów, czterysta "
                         "dziewięćdziesiąt osiem oktylionów, dwieście "
                         "czternaście septyliardy, osiemset "
                         "czterdzieści pięć septylionów, czterysta "
                         "dwadzieścia dziewięć sekstyliardów, czterysta "
                         "czterdzieści cztery sekstyliony, trzysta "
                         "trzydzieści sześć kwintyliardów, siedemset dwadzieścia "
                         "cztery kwintyliony, pięćset sześćdziesiąt dziewięć "
                         "kwadryliardów, trzysta siedemdziesiąt pięć "
                         "kwadrylionów, dwieście trzydzieści dziewięć sekstilionów,"
                         " sześćset siedemdziesiąt trylionów, pięćset "
                         "siedemdziesiąt cztery biliardy, siedemset "
                         "trzydzieści dziewięć bilionów, siedemset czterdzieści "
                         "osiem miliardów, czterysta siedemdziesiąt milionów, "
                         "dziewięćset piętnaście tysięcy, siedemdziesiąt dwa")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "nieskończoność")
        self.assertEqual(
            pronounce_number(float("inf")),
            "nieskończoność")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "minus nieskończoność")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "pierwszy")
        self.assertEqual(pronounce_number(10, ordinals=True), "dziesiąty")
        self.assertEqual(pronounce_number(15, ordinals=True), "piętnasty")
        self.assertEqual(pronounce_number(20, ordinals=True), "dwudziesty")
        self.assertEqual(pronounce_number(27, ordinals=True), "dwudziesty siódmy")
        self.assertEqual(pronounce_number(30, ordinals=True), "trzydziesty")
        self.assertEqual(pronounce_number(33, ordinals=True), "trzydziesty trzeci")
        self.assertEqual(pronounce_number(100, ordinals=True), "setny")
        self.assertEqual(pronounce_number(1000, ordinals=True), "tysięczny")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "dziesięcio tysięczny")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "osiemnaście tysięcy, sześćset dziewięćdziesiąty pierwszy")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "jeden tysiąc, pięćset sześćdziesiąty siódmy")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "jeden przecinek sześć siedem dwa razy dziesięć do "
                         "minus dwudziestej siódmej potęgi")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "osiemnasto milionowa")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "osiemnasto bilionowa")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "osiemnasto "
                                                              "trylionowa")


class TestNiceDateFormat(unittest.TestCase):
    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        self.assertEqual(nice_time(dt),
                         "trzynasta dwadzieścia dwa")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True),
                         "trzynasta dwadzieścia dwa")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "trzynasta zero zero")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True),
                         "trzynasta zero zero")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "trzynasta dwa")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trzynasta dwa")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dwa po północy")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "dwa po północy")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "pierwsza dwa")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "pierwsza dwa")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dwunasta piętnaście")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "pierwsza czterdzieści pięć")

    def test_nice_duration(self):
        self.assertEqual(nice_duration(1), "jedna sekunda")
        self.assertEqual(nice_duration(3), "trzy sekundy")
        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "jedna minuta jedna sekunda")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "jedna godzina dwadzieścia trzy minuty dwadzieścia sekund")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "trzynaście godzin pięćdziesiąt trzy minuty dwadzieścia sekund")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "pięć dni osiemnaście godzin pięćdziesiąt trzy minuty dwadzieścia sekund")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")


if __name__ == "__main__":
    unittest.main()
