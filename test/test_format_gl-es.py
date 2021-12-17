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

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import pronounce_number
from lingua_franca.time import default_timezone


def setUpModule():
    load_language('gl-es')
    set_default_lang('gl-es')


def tearDownModule():
    unload_language('gl-es')


NUMBERS_FIXTURE_GL-ES = {
    1.435634: '1,436',
    2: '2',
    5.0: '5',
    0.027: '0,027',
    0.5: 'un medio',
    1.333: '1 e 1 terzo',
    2.666: '2 e 2 terzo',
    0.25: 'un cuarto',
    1.25: '1 e 1 cuarto',
    0.75: '3 cuartos',
    1.75: '1 e 3 cuartos',
    3.4: '3 e 2 quintos',
    16.8333: '16 e 5 sextos',
    12.5714: '12 e 4 séptimos',
    9.625: '9 e 5 oitavos',
    6.777: '6 e 7 novenos',
    3.1: '3 e 1 décimo',
    2.272: '2 e 3 onceavos',
    5.583: '5 e 7 doceavos',
    8.384: '8 e 5 treceavos',
    0.071: 'un catorceavo',
    6.466: '6 e 7 quinceavos',
    8.312: '8 e 5 dezaseisavos',
    2.176: '2 e 3 dezaseteavos',
    200.722: '200 e 13 dezaoitoavos',
    7.421: '7 e 8 dezanoveavos',
    0.05: 'un vinteavo'

}


class TestNiceNumberFormat_gl-es(unittest.TestCase):
    def test_convert_float_to_nice_number_gl-es(self):
        for number, number_str in NUMBERS_FIXTURE_GL-ES.items():
            self.assertEqual(nice_number(number, lang="gl-es"), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(
                                     number, lang="gl-es")))

    def test_specify_denominator_gl-es(self):
        self.assertEqual(nice_number(5.5, lang="gl-es",
                                     denominators=[1, 2, 3]),
                         '5 e medio',
                         'should format 5.5 as 5 e medio not {}'.format(
                             nice_number(5.5, lang="gl-es",
                                         denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, lang="gl-es",
                                     denominators=[1, 2]),
                         '2,333',
                         'should format 2.333 as 2,333 not {}'.format(
                             nice_number(2.333, lang="gl-es",
                                         denominators=[1, 2])))

    def test_no_speech_gl-es(self):
        self.assertEqual(nice_number(6.777, lang="gl-es", speech=False),
                         '6 7/9',
                         'should format 6.777 as 6 7/9 not {}'.format(
                             nice_number(6.777, lang="gl-es", speech=False)))
        self.assertEqual(nice_number(6.0, lang="gl-es", speech=False),
                         '6',
                         'should format 6.0 as 6 not {}'.format(
                             nice_number(6.0, lang="gl-es", speech=False)))
        self.assertEqual(nice_number(1234567890, lang="gl-es", speech=False),
                         '1 234 567 890',
                         'should format 1234567890 as'
                         '1 234 567 890 not {}'.format(
                             nice_number(1234567890, lang="gl-es",
                                         speech=False)))
        self.assertEqual(nice_number(12345.6789, lang="gl-es", speech=False),
                         '12 345,679',
                         'should format 12345.6789 as'
                         '12 345,679 not {}'.format(
                             nice_number(12345.6789, lang="gl-es",
                                         speech=False)))


class TestPronounceNumber(unittest.TestCase):
    def test_convert_int(self):
        self.assertEqual(pronounce_number(0, lang="gl-es"), "cero")
        self.assertEqual(pronounce_number(1, lang="gl-es"), "un")
        self.assertEqual(pronounce_number(10, lang="gl-es"), "dez")
        self.assertEqual(pronounce_number(15, lang="gl-es"), "quince")
        self.assertEqual(pronounce_number(21, lang="gl-es"), "vinte e un")
        self.assertEqual(pronounce_number(27, lang="gl-es"), "vinte e sete")
        self.assertEqual(pronounce_number(30, lang="gl-es"), "trinta")
        self.assertEqual(pronounce_number(19, lang="gl-es"), "dezanove")
        self.assertEqual(pronounce_number(88, lang="gl-es"), "oitenta e oito")
        self.assertEqual(pronounce_number(46, lang="gl-es"), "corenta e seis")
        self.assertEqual(pronounce_number(99, lang="gl-es"), "noventa e nove")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1, lang="gl-es"), "menos un")
        self.assertEqual(pronounce_number(-10, lang="gl-es"), "menos dez")
        self.assertEqual(pronounce_number(-15, lang="gl-es"), "menos quince")
        self.assertEqual(pronounce_number(-21, lang="gl-es"), "menos vinte e un")
        self.assertEqual(pronounce_number(-27, lang="gl-es"), "menos vinte e sete")
        self.assertEqual(pronounce_number(-30, lang="gl-es"), "menos trinta")
        self.assertEqual(pronounce_number(-35, lang="gl-es"),
                         "menos trinta e cinco")
        self.assertEqual(pronounce_number(-83, lang="gl-es"),
                         "menos oitenta e tres")
        self.assertEqual(pronounce_number(-19, lang="gl-es"), "menos dezanove")
        self.assertEqual(pronounce_number(-88, lang="gl-es"),
                         "menos oitenta e oito")
        self.assertEqual(pronounce_number(-46, lang="gl-es"),
                         "menos corenta e seis")
        self.assertEqual(pronounce_number(-99, lang="gl-es"),
                         "menos noventa e nove")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(
            0.05, lang="gl-es"), "cero coma cero cinco")
        self.assertEqual(pronounce_number(
            -0.05, lang="gl-es"), "menos cero coma cero cinco")
        self.assertEqual(pronounce_number(1.234, lang="gl-es"),
                         "uno coma dous tres catro")
        self.assertEqual(pronounce_number(21.234, lang="gl-es"),
                         "vinte e un coma dous tres")
        self.assertEqual(pronounce_number(21.234, lang="gl-es", places=1),
                         "vinte e un coma dous")
        self.assertEqual(pronounce_number(21.234, lang="gl-es", places=0),
                         "vinte e un")
        self.assertEqual(pronounce_number(21.234, lang="gl-es", places=3),
                         "vinte e un coma dous tres catro")
        self.assertEqual(pronounce_number(21.234, lang="gl-es", places=4),
                         "vinte e un coma dous tres catro")
        self.assertEqual(pronounce_number(21.234, lang="gl-es", places=5),
                         "vinte e un coma dous tres catro")
        self.assertEqual(pronounce_number(-21.234, lang="gl-es"),
                         "menos vinte e un coma dous tres")
        self.assertEqual(pronounce_number(-21.234, lang="gl-es", places=1),
                         "menos vinte e un coma dous")
        self.assertEqual(pronounce_number(-21.234, lang="gl-es", places=0),
                         "menos vinte e un")
        self.assertEqual(pronounce_number(-21.234, lang="gl-es", places=3),
                         "menos vinte e un coma dous tres catro")
        self.assertEqual(pronounce_number(-21.234, lang="gl-es", places=4),
                         "menos vinte e un coma dous tres catro")
        self.assertEqual(pronounce_number(-21.234, lang="gl-es", places=5),
                         "menos vinte e un coma dous tres catro")


class TestNiceDateFormat(unittest.TestCase):
    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         nice_time(dt, "gl-es", True, False, False))

        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "a unha e vinte e dous")
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "a unha e vinte e dous da tarde")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True), "as trece vinte e dous")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=False), "as trece vinte e dous")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "a unha en punto")
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "a unha da tarde")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True), "as trece cero cero")
        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True),
                         "as trece cero dous")
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "a unha e dúas de la tarde")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True), "as trece cero dous")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=False), "as trece cero dous")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as doce e dúas")
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "as doce e dúas da madrugada")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True),
                         "as cero cero dous")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True), "as cero cero dous")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=False), "as cero cero dous")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as doce e cuarto")
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "as doce e cuarto da mañá")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True),
                         "as doce quince")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=False),
                         "as doce quince")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as oito menos vinte")
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "as oito menos vinte da tarde")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="gl-es", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True),
                         "as dezanove corenta")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=False),
                         "as dezanove corenta")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True),
                         "a unha quince")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as dúas menos vinte e cinco")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as dúas menos cuarto")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as cinco menos dez")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es"),
                         "as seis menos cinco")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es", use_ampm=True),
                         "as cinco e media da madrugada")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=True,
                                   use_ampm=True),
                         "as vinte e tres quince")
        self.assertEqual(nice_time(dt, lang="gl-es", use_24hour=False,
                                   use_ampm=True),
                         "as once e cuarto da noche")


if __name__ == "__main__":
    unittest.main()
