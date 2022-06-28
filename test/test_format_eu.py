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
from lingua_franca.time import now_local
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import nice_relative_time
from lingua_franca.format import pronounce_number

# https://www.euskaltzaindia.eus/index.php?&option=com_ebe&view=bilaketa&Itemid=1161&task=bilaketa&lang=eu&id=1392


def setUpModule():
    load_language('eu')
    set_default_lang('eu')


def tearDownModule():
    unload_language('eu')


NUMBERS_FIXTURE_EU = {
    1.435634: '1,436',
    2: '2',
    5.0: '5',
    0.027: '0,027',
    0.5: 'erdi bat',
    1.333: '1 eta heren bat',
    2.666: '2 eta 2 heren',
    0.25: 'laurden bat',
    1.25: '1 eta laurden bat',
    0.75: '3 laurden',
    1.75: '1 eta 3 laurden',
    3.4: '3 eta 2 bosten',
    16.8333: '16 eta 5 seiren',
    12.5714: '12 eta 4 zazpiren',
    9.625: '9 eta 5 zortziren',
    6.777: '6 eta 7 bederatziren',
    3.1: '3 eta hamarren bat',
    2.272: '2 eta 3 hamaikaren',
    5.583: '5 eta 7 hamabiren',
    8.384: '8 eta 5 hamahiruren',
    0.071: 'hamalauren bat',
    6.466: '6 eta 7 hamabosten',
    8.312: '8 eta 5 hamaseiren',
    2.176: '2 eta 3 hamazazpiren',
    200.722: '200 eta 13 hemezortziren',
    7.421: '7 eta 8 hemeretziren',
    0.05: 'hogeiren bat'

}


class TestNiceNumberFormat_eu(unittest.TestCase):
    def test_convert_float_to_nice_number_eu(self):
        for number, number_str in NUMBERS_FIXTURE_EU.items():
            self.assertEqual(nice_number(number, lang="eu-eu"), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(
                                     number, lang="eu-eu")))

    def test_specify_denominator_eu(self):
        self.assertEqual(nice_number(5.5, lang="eu-eu",
                                     denominators=[1, 2, 3]),
                         '5 eta erdi',
                         'should format 5.5 as 5 eta erdi not {}'.format(
                             nice_number(5.5, lang="eu-eu",
                                         denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, lang="eu-eu",
                                     denominators=[1, 2]),
                         '2,333',
                         'should format 2.333 as 2,333 not {}'.format(
                             nice_number(2.333, lang="eu-eu",
                                         denominators=[1, 2])))

    def test_no_speech_eu(self):
        self.assertEqual(nice_number(6.777, lang="eu-eu", speech=False),
                         '6 7/9',
                         'should format 6.777 as 6 7/9 not {}'.format(
                             nice_number(6.777, lang="eu-eu", speech=False)))
        self.assertEqual(nice_number(6.0, lang="eu-eu", speech=False),
                         '6',
                         'should format 6.0 as 6 not {}'.format(
                             nice_number(6.0, lang="eu-eu", speech=False)))
        self.assertEqual(nice_number(1234567890, lang="eu-eu", speech=False),
                         '1 234 567 890',
                         'should format 1234567890 as'
                         '1 234 567 890 not {}'.format(
                             nice_number(1234567890, lang="eu-eu",
                                         speech=False)))
        self.assertEqual(nice_number(12345.6789, lang="eu-eu", speech=False),
                         '12 345,679',
                         'should format 12345.6789 as'
                         '12 345,679 not {}'.format(
                             nice_number(12345.6789, lang="eu-eu",
                                         speech=False)))


# https://www.euskaltzaindia.eus/dok/arauak/Araua_0007.pdf

class TestPronounceNumber(unittest.TestCase):
    def test_convert_int(self):
        # self.assertEqual(pronounce_number(0, lang="eu"), "zero")
        self.assertEqual(pronounce_number(1, lang="eu"), "bat")
        self.assertEqual(pronounce_number(10, lang="eu"), "hamar")
        self.assertEqual(pronounce_number(15, lang="eu"), "hamabost")
        self.assertEqual(pronounce_number(21, lang="eu"), "hogeita bat")
        self.assertEqual(pronounce_number(27, lang="eu"), "hogeita zazpi")
        self.assertEqual(pronounce_number(30, lang="eu"), "hogeita hamar")
        self.assertEqual(pronounce_number(19, lang="eu"), "hemeretzi")
        self.assertEqual(pronounce_number(88, lang="eu"), "laurogeita zortzi")
        self.assertEqual(pronounce_number(46, lang="eu"), "berrogeita sei")
        self.assertEqual(pronounce_number(99, lang="eu"), "laurogeita hemeretzi")
        self.assertEqual(pronounce_number(399, lang="eu"), "hirurehun eta laurogeita hemeretzi")
        self.assertEqual(pronounce_number(1200, lang="eu"), "mila eta berrehun")
        self.assertEqual(pronounce_number(1202, lang="eu"), "mila berrehun eta bi")
        self.assertEqual(pronounce_number(1359, lang="eu"), "mila hirurehun eta berrogeita hemeretzi")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1, lang="eu"), "minus bat")
        self.assertEqual(pronounce_number(-10, lang="eu"), "minus hamar")
        self.assertEqual(pronounce_number(-15, lang="eu"), "minus hamabost")
        self.assertEqual(pronounce_number(-21, lang="eu"), "minus hogeita bat")
        self.assertEqual(pronounce_number(-27, lang="eu"), "minus hogeita zazpi")
        self.assertEqual(pronounce_number(-30, lang="eu"), "minus hogeita hamar")
        self.assertEqual(pronounce_number(-35, lang="eu"),
                         "minus hogeita hamabost")
        self.assertEqual(pronounce_number(-83, lang="eu"),
                         "minus laurogeita hiru")
        self.assertEqual(pronounce_number(-19, lang="eu"), "minus hemeretzi")
        self.assertEqual(pronounce_number(-88, lang="eu"),
                         "minus laurogeita zortzi")
        self.assertEqual(pronounce_number(-46, lang="eu"),
                         "minus berrogeita sei")
        self.assertEqual(pronounce_number(-99, lang="eu"),
                         "minus laurogeita hemeretzi")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(
            0.05, lang="eu"), "zero koma zero bost")
        self.assertEqual(pronounce_number(
            -0.05, lang="eu"), "minus zero koma zero bost")
        self.assertEqual(pronounce_number(1.234, lang="eu"),
                         "bat koma bi hiru")
        self.assertEqual(pronounce_number(21.234, lang="eu"),
                         "hogeita bat koma bi hiru")
        self.assertEqual(pronounce_number(21.234, lang="eu", places=1),
                         "hogeita bat koma bi")
        self.assertEqual(pronounce_number(21.234, lang="eu", places=0),
                         "hogeita bat")
        self.assertEqual(pronounce_number(21.234, lang="eu", places=3),
                         "hogeita bat koma bi hiru lau")
        self.assertEqual(pronounce_number(21.234, lang="eu", places=4),
                         "hogeita bat koma bi hiru lau")
        self.assertEqual(pronounce_number(21.234, lang="eu", places=5),
                         "hogeita bat koma bi hiru lau")
        self.assertEqual(pronounce_number(-21.234, lang="eu"),
                         "minus hogeita bat koma bi hiru")
        self.assertEqual(pronounce_number(-21.234, lang="eu", places=1),
                         "minus hogeita bat koma bi")
        self.assertEqual(pronounce_number(-21.234, lang="eu", places=0),
                         "minus hogeita bat")
        self.assertEqual(pronounce_number(-21.234, lang="eu", places=3),
                         "minus hogeita bat koma bi hiru lau")
        self.assertEqual(pronounce_number(-21.234, lang="eu", places=4),
                         "minus hogeita bat koma bi hiru lau")
        self.assertEqual(pronounce_number(-21.234, lang="eu", places=5),
                         "minus hogeita bat koma bi hiru lau")


class TestNiceDateFormat(unittest.TestCase):
    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3)

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         nice_time(dt, "eu-eu", True, False, False))

        self.assertEqual(nice_time(dt, lang="eu"),
                         "ordubata eta hogeita bi")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "arratsaldeko ordubata eta hogeita bi")
        self.assertEqual(nice_time(dt, lang="eu", speech=False), "1:22")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "1:22 PM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "13:22")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True, use_ampm=True), "13:22")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "hamahiruak hogeita bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=False), "hamahiruak hogeita bi")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3)
        self.assertEqual(nice_time(dt, lang="eu"),
                         "ordubata puntuan")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "arratsaldeko ordubata")
        self.assertEqual(nice_time(dt, lang="eu", speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "1:00 PM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "13:00")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True, use_ampm=True), "13:00")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "hamahiruak zero zero")
        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3)
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True),
                         "hamahiruak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "arratsaldeko ordubata eta bi")
        self.assertEqual(nice_time(dt, lang="eu", speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "1:02 PM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "13:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True, use_ampm=True), "13:02")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "hamahiruak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=False), "hamahiruak zero bi")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3)
        self.assertEqual(nice_time(dt, lang="eu"),
                         "hamabiak eta bi")
        self.assertEqual(nice_time(dt, lang="eu", use_ampm=True),
                         "gaueko hamabiak eta bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True),
                         "zeroak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_ampm=True), "12:02 AM")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True), "00:02")
        self.assertEqual(nice_time(dt, lang="eu", speech=False,
                                   use_24hour=True,
                                   use_ampm=True), "00:02")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=True), "zeroak zero bi")
        self.assertEqual(nice_time(dt, lang="eu", use_24hour=True,
                                   use_ampm=False), "zeroak zero bi")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "hamabiak eta laurden")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_ampm=True),
                         "goizeko hamabiak eta laurden")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_ampm=True),
                         "12:15 PM")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "12:15")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=True),
                         "hamabiak hamabost")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=False),
                         "hamabiak hamabost")

        dt = datetime.datetime(2017, 1, 31,
                               19, 40, 49)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "zortzirak hogei gutxi")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_ampm=True),
                         "arratsaldeko zortzirak hogei gutxi")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False),
                         "7:40")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_ampm=True),
                         "7:40 PM")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="eu-eu", speech=False,
                                   use_24hour=True, use_ampm=True),
                         "19:40")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=True),
                         "hemeretziak berrogei")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=False),
                         "hemeretziak berrogei")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True),
                         "batak hamabost")

        dt = datetime.datetime(2017, 1, 31,
                               1, 35, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "ordubiak hogeita bost gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "ordubiak laurden gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               4, 50, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "bostak hamar gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               5, 55, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu"),
                         "seirak bost gutxi")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00)
        self.assertEqual(nice_time(dt, lang="eu-eu", use_ampm=True),
                         "gaueko bostak eta erdi")

        dt = datetime.datetime(2017, 1, 31,
                               23, 15, 9)
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=True,
                                   use_ampm=True),
                         "hogeita hiruak hamabost")
        self.assertEqual(nice_time(dt, lang="eu-eu", use_24hour=False,
                                   use_ampm=True),
                         "gaueko hamaikak eta laurden")


class TestNiceRelativeTime(unittest.TestCase):
    def test_format_nice_relative_time(self):
        now = now_local()
        two_hours_from_now = now + datetime.timedelta(hours=2)
        self.assertEqual(
            nice_relative_time(when=two_hours_from_now, relative_to=now),
            "2 ordu"
        )
        seconds_from_now = now + datetime.timedelta(seconds=47)
        self.assertEqual(
            nice_relative_time(when=seconds_from_now, relative_to=now),
            "47 segundo"
        )
        days_from_now = now + datetime.timedelta(days=3)
        self.assertEqual(
            nice_relative_time(when=days_from_now, relative_to=now),
            "3 egun"
        )


if __name__ == "__main__":
    unittest.main()
