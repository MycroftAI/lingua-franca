#
# Copyright 2019 Mycroft AI Inc.
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

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.format import nice_time
from lingua_franca.format import pronounce_number
from lingua_franca.lang.format_ca import TimeVariantCA
from lingua_franca.time import default_timezone


def setUpModule():
    load_language('ca-es')
    set_default_lang('ca')


def tearDownModule():
    unload_language('ca')


NUMBERS_FIXTURE_CA = {
    1.435634: '1,436',
    2: '2',
    5.0: '5',
    0.027: '0,027',
    0.5: 'un mig',
    1.333: '1 i 1 terç',
    2.666: '2 i 2 terços',
    0.25: 'un quart',
    1.25: '1 i 1 quart',
    0.75: '3 quarts',
    1.75: '1 i 3 quarts',
    3.4: '3 i 2 cinquens',
    16.8333: '16 i 5 sisens',
    12.5714: '12 i 4 setens',
    9.625: '9 i 5 vuitens',
    6.777: '6 i 7 novens',
    3.1: '3 i 1 desè',
    2.272: '2 i 3 onzens',
    5.583: '5 i 7 dotzens',
    8.384: '8 i 5 tretzens',
    0.071: 'catorzens',
    6.466: '6 i 7 quinzens',
    8.312: '8 i 5 setzens',
    2.176: '2 i 3 dissetens',
    200.722: '200 i 13 divuitens',
    7.421: '7 i 8 dinovens',
    0.05: 'un vintè'

}


class TestPronounceNumber(unittest.TestCase):
    def test_convert_int(self):
        self.assertEqual(pronounce_number(0, lang="ca"), "zero")
        self.assertEqual(pronounce_number(1, lang="ca"), "un")
        self.assertEqual(pronounce_number(10, lang="ca"), "deu")
        self.assertEqual(pronounce_number(15, lang="ca"), "quinze")
        self.assertEqual(pronounce_number(21, lang="ca"), "vint-i-un")
        self.assertEqual(pronounce_number(27, lang="ca"), "vint-i-set")
        self.assertEqual(pronounce_number(30, lang="ca"), "trenta")
        self.assertEqual(pronounce_number(19, lang="ca"), "dinou")
        self.assertEqual(pronounce_number(88, lang="ca"), "vuitanta-vuit")
        self.assertEqual(pronounce_number(46, lang="ca"), "quaranta-sis")
        self.assertEqual(pronounce_number(99, lang="ca"), "noranta-nou")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1, lang="ca"), "menys un")
        self.assertEqual(pronounce_number(-10, lang="ca"), "menys deu")
        self.assertEqual(pronounce_number(-15, lang="ca"), "menys quinze")
        self.assertEqual(pronounce_number(-21, lang="ca"), "menys vint-i-un")
        self.assertEqual(pronounce_number(-27, lang="ca"),
                         "menys vint-i-set")
        self.assertEqual(pronounce_number(-30, lang="ca"), "menys trenta")
        self.assertEqual(pronounce_number(-35, lang="ca"),
                         "menys trenta-cinc")
        self.assertEqual(pronounce_number(-83, lang="ca"),
                         "menys vuitanta-tres")
        self.assertEqual(pronounce_number(-19, lang="ca"), "menys dinou")
        self.assertEqual(pronounce_number(-88, lang="ca"),
                         "menys vuitanta-vuit")
        self.assertEqual(pronounce_number(-46, lang="ca"),
                         "menys quaranta-sis")
        self.assertEqual(pronounce_number(-99, lang="ca"),
                         "menys noranta-nou")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(
            0.05, lang="ca"), "zero coma zero cinc")
        self.assertEqual(pronounce_number(
            -0.05, lang="ca"), "menys zero coma zero cinc")
        self.assertEqual(pronounce_number(1.234, lang="ca"),
                         "un coma dos tres")
        self.assertEqual(pronounce_number(21.234, lang="ca"),
                         "vint-i-un coma dos tres")
        self.assertEqual(pronounce_number(21.234, lang="ca", places=1),
                         "vint-i-un coma dos")
        self.assertEqual(pronounce_number(21.234, lang="ca", places=0),
                         "vint-i-un")
        self.assertEqual(pronounce_number(21.234, lang="ca", places=3),
                         "vint-i-un coma dos tres quatre")
        self.assertEqual(pronounce_number(21.234, lang="ca", places=4),
                         "vint-i-un coma dos tres quatre")
        self.assertEqual(pronounce_number(20.234, lang="ca", places=5),
                         "vint coma dos tres quatre")
        self.assertEqual(pronounce_number(-21.234, lang="ca"),
                         "menys vint-i-un coma dos tres")
        self.assertEqual(pronounce_number(-21.234, lang="ca", places=1),
                         "menys vint-i-un coma dos")
        self.assertEqual(pronounce_number(-21.234, lang="ca", places=0),
                         "menys vint-i-un")
        self.assertEqual(pronounce_number(-21.234, lang="ca", places=3),
                         "menys vint-i-un coma dos tres quatre")
        self.assertEqual(pronounce_number(-21.234, lang="ca", places=4),
                         "menys vint-i-un coma dos tres quatre")
        self.assertEqual(pronounce_number(-21.234, lang="ca", places=5),
                         "menys vint-i-un coma dos tres quatre")


class TestNiceDateFormat(unittest.TestCase):
    def test_pm(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         nice_time(dt, "ca-es", True, False, False))

        self.assertEqual(nice_time(dt, lang="ca"), "la una i vint-i-dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una i vint-i-dos de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze i vint-i-dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les tretze i vint-i-dos")

        dt = datetime.datetime(2017, 1, 31, 
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca"), "la una en punt")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una en punt de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:00")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze")

        dt = datetime.datetime(2017, 1, 31, 
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True),
                         "les tretze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "la una i dos de la tarda")
        self.assertEqual(nice_time(dt, lang="ca", speech=False), "1:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les tretze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les tretze i dos")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 0, tzinfo=default_timezone())
        # Default Watch system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les dotze i quinze")
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i quart")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "un quart d'una de la tarda")
        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "un quart d'una de la tarda")

        dt = datetime.datetime(2017, 1, 31,
                               00, 14, 0, tzinfo=default_timezone())
        # Default Watch system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les zero i catorze")
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.SPANISH_LIKE),
                         "les dotze i catorze")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant=TimeVariantCA.BELL),
                         "les dotze i catorze minuts de la nit")
        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant=TimeVariantCA.FULL_BELL),
                         "un quart d'una de la matinada")

    def test_midnight(self):
        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca"),
                         "les dotze i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_ampm=True),
                         "les dotze i dos de la nit")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True),
                         "les zero i dos")
        self.assertEqual(nice_time(dt, lang="ca", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="ca", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=True), "les zero i dos")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False), "les zero i dos")

    def test_midday(self):
        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les dotze i quinze del migdia")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=False),
                         "les dotze i quinze")

    def test_minutes_to_hour(self):
        # "twenty minutes to midnight"
        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les set i quaranta")
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les set i quaranta del vespre")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="ca-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les dinou i quaranta")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=False),
                         "les dinou i quaranta")

    def test_minutes_past_hour(self):
        # "quarter past ten"
        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True),
                         "la una i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i quinze")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i trenta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "la una i quaranta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les quatre i cinquanta")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es"),
                         "les cinc i cinquanta-cinc")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_ampm=True),
                         "les cinc i trenta de la matinada")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=True,
                                   use_ampm=True),
                         "les vint-i-tres i quinze")
        self.assertEqual(nice_time(dt, lang="ca-es", use_24hour=False,
                                   use_ampm=True),
                         "les onze i quinze de la nit")

    def test_variant_strings(self):
        dt = datetime.datetime(2017, 1, 31, 
                               12, 15, 0, tzinfo=default_timezone())
        # Default variant
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant="default"),
                         "les dotze i quinze")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False),
                         "les dotze i quinze")

        dt = datetime.datetime(2017, 1, 31, 
                               00, 14, 0, tzinfo=default_timezone())
        # Spanish-like time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant="spanish"),
                         "les dotze i catorze")
        # Catalan Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False, variant="bell"),
                         "les dotze i catorze minuts de la nit")

        # Catalan Full Bell time system
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant="full_bell"),
                         "un quart d'una de la matinada")
        self.assertEqual(nice_time(dt, lang="ca", use_24hour=True,
                                   use_ampm=False,
                                   variant="traditional"),
                         "un quart d'una de la matinada")

        # error
        with self.assertRaises(ValueError):
            nice_time(dt, lang="ca", variant="invalid")
            nice_time(dt, lang="ca", variant="bad_VARIANT")
            nice_time(dt, lang="ca", variant="")


if __name__ == "__main__":
    unittest.main()
