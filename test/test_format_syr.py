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
import warnings
import sys
from pathlib import Path

# TODO either write a getter for lingua_franca.internal._SUPPORTED_LANGUAGES,
# or make it public somehow
from lingua_franca import load_languages, unload_languages, set_default_lang, \
    get_primary_lang_code, get_active_langs, get_supported_langs
from lingua_franca.internal import UnsupportedLanguageError
from lingua_franca.format import nice_number
from lingua_franca.format import nice_time
from lingua_franca.format import nice_date
from lingua_franca.format import nice_date_time
from lingua_franca.format import nice_year
from lingua_franca.format import nice_duration
from lingua_franca.format import pronounce_number
from lingua_franca.format import date_time_format
from lingua_franca.format import join_list


def setUpModule():
    load_languages(get_supported_langs())
    # TODO spin English tests off into another file, like other languages, so we
    # don't have to do this confusing thing in the "master" test_format.py
    set_default_lang('syr-sy')


def tearDownModule():
    unload_languages(get_active_langs())


NUMBERS_FIXTURE_EN = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: 'ܦܠܓܗ ',
    1.333: '1 ܘܬܘܠܬܐ',
    2.666: '2 ܘܬܪܝܢ ܡ̣ܢ ܬܠܬܐ ',
    0.25: 'ܪܘܒܥܐ',
    1.25: '1 ܘܪܘܒܥܐ',
    0.75: 'ܪ̈ܘܒܥܐ 3',
    1.75: '1 ܘ3 ܪ̈ܘܒܥܐ',
    3.4: '3 ܘܬܪܝܢ ܡ̣ܢ ܚܡܫܐ',
    16.8333: '16 ܘ5 ܡ̣ܢ ܫܬܐ',
    12.5714: '12 ܘ4 ܡ̣ܢ ܫܒ̣ܥܐ',
    9.625: '9 ܘ5 ܡ̣ܢ ܬܡܢܝܐ',
    6.777: '6 ܘ7 ܡ̣ܢ ܬܫܥܐ',
    3.1: '3 ܘܚܕ ܡ̣ܢ ܥܣܪܐ',
    2.272: '2 ܘ3 ܡ̣ܢ ܚܕܥܣܝܪܝܐ',
    5.583: '5 ܘ7 ܡ̣ܢ ܬܪܥܣܝܪܝܐ',
    8.384: '8 ܘ5 ܡ̣ܢ ܬܠܬܥܣܝܪܝܐ',
    0.071: 'ܚܕ ܡ̣ܢ ܐܪܒܥܣܝܪܝܐ',
    6.466: '6 ܘ7 ܡ̣ܢ ܚܡܫܥܣܝܪܝܐ',
    8.312: '8 ܘ5 ܡ̣ܢ ܫܬܥܣܝܪܝܐ',
    2.176: '2 ܘ3 ܡ̣ܢ ܫܒܥܣܝܪܝܐ',
    200.722: '200 ܘ13 ܡ̣ܢ ܬܡܢܥܣܝܪܝܐ',
    7.421: '7 ܘ8 ܡ̣ܢ ܬܫܥܣܝܪܝܐ',
    0.05: 'ܚܕ ܡ̣ܢ ܥܣܪܝܢܝܐ'
}


class TestNiceNumberFormat(unittest.TestCase):

    tmp_var = None

    def set_tmp_var(self, val):
        self.tmp_var = val

    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_EN.items():
            self.assertEqual(nice_number(number), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(number)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, denominators=[1, 2, 3]),
                         '5 ܘܦܠܓܗ',
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
        self.assertEqual(pronounce_number(0),  "ܣܝܦܪ")
        self.assertEqual(pronounce_number(1),  "ܚܕ")
        self.assertEqual(pronounce_number(10), "ܥܣܪܐ")
        self.assertEqual(pronounce_number(15), "ܚܡܫܥܣܪ")
        self.assertEqual(pronounce_number(20), "ܥܣܪܝܢ")
        self.assertEqual(pronounce_number(27), "ܥܣܪܝܢ ܘܫܒܥܐ")
        self.assertEqual(pronounce_number(30), "ܬܠܬܝܢ")
        self.assertEqual(pronounce_number(33), "ܬܠܬܝܢ ܘܬܠܬܐ")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1),  "ܣܚܘܦܐ ܚܕ")
        self.assertEqual(pronounce_number(-10), "ܣܚܘܦܐ ܥܣܪܐ")
        self.assertEqual(pronounce_number(-15), "ܣܚܘܦܐ ܚܡܫܝܣܪ")
        self.assertEqual(pronounce_number(-20), "ܣܚܘܦܐ ܥܣܪܝܢ")
        self.assertEqual(pronounce_number(-27), "ܣܚܘܦܐ ܥܣܪܝܢ ܘܫܒܥܐ")
    
    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "ܚܡܫܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(-0.05), "ܣܚܘܦܐ ܚܡܫܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(1.234),
                         "ܚܕ̄ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(21.234),
                         "ܥܣܪܝܢ ܘܚܕ̄ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "ܥܣܪܝܢ ܘܚܕ̄ ܘܥܣܪܝܢ ܘܬܪܝܢ ܡܢ ܥܣܪܐ")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "ܥܣܪܝܢ ܘܚܕ̄")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "ܥܣܪܝܢ ܘܚܕ̄ ܘܬܪܝܡܐܐ ܘܬܠܬܝܢ ܘܐܪܒܥܐ ܡܢ ܐܠܦܐ")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "ܥܣܪܝܢ ܘܚܕ̄ ܘܬܪܝܡܐܐ ܘܬܠܬܝܢ ܘܐܪܒܥܐ ܡܢ ܐܠܦܐ")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "ܥܣܪܝܢ ܘܚܕ̄ ܘܬܪܝܡܐܐ ܘܬܠܬܝܢ ܘܐܪܒܥܐ ܡܢ ܐܠܦܐ")
        self.assertEqual(pronounce_number(-1.234),
                         "ܣܚܘܦܐ ܚܕ̄ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(-21.234),
                         "ܣܚܘܦܐ ܥܣܪܝܢ ܘܚܕ̄ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "ܣܚܘܦܐ ܥܣܪܝܢ ܘܚܕ̄ ܘܥܣܪܝܢ ܘܬܪܝܢ ܡܢ ܥܣܪܐ")

    def test_convert_hundreds(self):
        self.assertEqual(pronounce_number(100), "ܡܐܐ")
        self.assertEqual(pronounce_number(666), "ܫܬܡܐܐ ܘ ܫܬܝܢ ܘܫܬܐ")
        self.assertEqual(pronounce_number(1456), "ܐܠܦܐ ܘܐܪܒܥܡܐܐ ܘܚܡܫܝܢ ܘܫܬܐ")
        self.assertEqual(pronounce_number(103254654), "صد و سه میلیون و "
                                                      "دویست و پنجاه و چهار "
                                                      "هزار و ششصد و پنجاه و چهار")
        self.assertEqual(pronounce_number(1512457), "یک میلیون و پانصد و دوازده هزار"
                                                    " و چهارصد و پنجاه و هفت")
        self.assertEqual(pronounce_number(209996), "دویست و نه هزار و نهصد و نود و شش")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "صفر")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "سه و سه دهم ضرب در ده به توان یک")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "دو و نود و نه صدم ضرب در ده به توان هشت")
        self.assertEqual(pronounce_number(299792448, places=6,
                                          scientific=True),
                         "دو و نهصد و نود و هفت هزار و نهصد و بیست و چهار میلیونیم ضرب در ده به توان هشت")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "یک و ششصد و هفتاد و دو هزارم ضرب در ده به توان منفی بیست و هفت")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "یکم")
        self.assertEqual(pronounce_number(10, ordinals=True), "دهم")
        self.assertEqual(pronounce_number(15, ordinals=True), "پونزدهم")
        self.assertEqual(pronounce_number(20, ordinals=True), "بیستم")
        self.assertEqual(pronounce_number(27, ordinals=True), "بیست و هفتم")
        self.assertEqual(pronounce_number(30, ordinals=True), "سیم")
        self.assertEqual(pronounce_number(33, ordinals=True), "سی و سوم")
        self.assertEqual(pronounce_number(100, ordinals=True), "صدم")
        self.assertEqual(pronounce_number(1000, ordinals=True), "هزارم")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "ده هزارم")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "هیجده هزار و ششصد و نود و یکم")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "هزار و پانصد و شصت و هفتم")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "هیجده میلیونم")
        self.assertEqual(pronounce_number(18e9, ordinals=True),
                         "هیجده میلیاردم")
    def test_variant(self):
        self.assertEqual(pronounce_number(18691, ordinals=True, variant="formal"),
            "هجده هزار و ششصد و نود و یکم")
        self.assertEqual(pronounce_number(15, variant='conversational'), "پونزده")
        self.assertEqual(pronounce_number(15, variant='formal'), "پانزده")
        self.assertEqual(nice_number(2.176, variant='formal'), "2 و 3 هفدهم")
        dt = datetime.datetime(2017, 1, 31,
                               16, 22, 3)
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True, variant='formal'),
                         "شانزده و بیست و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True, variant='conversational'),
                         "شونزده و بیست و دو دقیقه")
        


# def nice_time(dt, lang="en-us", speech=True, use_24hour=False,
#              use_ampm=False):

class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            if (sub_dir / 'date_time_test.json').exists():
                print("Getting test for " +
                      str(sub_dir / 'date_time_test.json'))
                with (sub_dir / 'date_time_test.json').open() as f:
                    cls.test_config[sub_dir.parts[-1]] = json.loads(f.read())
    

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3)

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, "fa-ir", True, False, False))

        self.assertEqual(nice_time(dt),
                         "یک و بیست و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک و بیست و دو دقیقه بعد از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "سیزده و بیست و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "سیزده و بیست و دو دقیقه")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3)
        self.assertEqual(nice_time(dt),
                         "یک")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک بعد از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "سیزده")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "سیزده")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3)
        self.assertEqual(nice_time(dt),
                         "یک و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک و دو دقیقه بعد از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "سیزده و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "سیزده و دو دقیقه")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3)
        self.assertEqual(nice_time(dt),
                         "دوازده و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "دوازده و دو دقیقه قبل از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "صفر و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "صفر و دو دقیقه")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33)
        self.assertEqual(nice_time(dt),
                         "یک و دو دقیقه")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "یک و دو دقیقه قبل از ظهر")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "یک و دو دقیقه")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "یک و دو دقیقه")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9)
        self.assertEqual(nice_time(dt),
                         "دوازده و ربع")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "دوازده و ربع بعد از ظهر")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00)
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "پنج و نیم قبل از ظهر")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00)
        self.assertEqual(nice_time(dt),
                         "یه ربع به دو")

    # TODO: failed because of و
    #def test_nice_duration(self):
    #    self.assertEqual(nice_duration(1), "یک ثانیه")
    #    self.assertEqual(nice_duration(3), "سه ثانیه")
    #    self.assertEqual(nice_duration(1, speech=False), "0:01")
    #    self.assertEqual(nice_duration(61), "یک دقیقه و یک ثانیه")
    #    self.assertEqual(nice_duration(61, speech=False), "1:01")
    #    self.assertEqual(nice_duration(5000),
    #                     "یک ساعت و بیست و سه دقیقه و بیست ثانیه")
    #    self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
    #    self.assertEqual(nice_duration(50000),
    #                     "سیزده ساعت و پنجاه و سه دقیقه و بیست ثانیه")
    #    self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
    #    self.assertEqual(nice_duration(500000),
    #                     "پنج روز و هیجده ساعت و پنجاه و سه دقیقه و بیست ثانیه")  # nopep8
    #    self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
    #    self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
    #                                   speech=False),
    #                     "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "and"), "")
        self.assertEqual(join_list([], "and"), "")

        self.assertEqual(join_list(["الف"], "و"), "الف")
        self.assertEqual(join_list(["الف", "ب"], "و"), "الف و ب")
        self.assertEqual(join_list(["الف", "ب"], "یا"), "الف یا ب")

        self.assertEqual(join_list(["الف", "ب", "ج"], "و"), "الف, ب و ج")
        self.assertEqual(join_list(["الف", "ب", "ج"], "یا"), "الف, ب یا ج")
        self.assertEqual(join_list(["الف", "ب", "ج"], "یا", ";"), "الف; ب یا ج")
        self.assertEqual(join_list(["الف", "ب", "ج", "دال"], "یا"), "الف, ب, ج یا دال")

        self.assertEqual(join_list([1, "ب", 3, "دال"], "یا"), "1, ب, 3 یا دال")


if __name__ == "__main__":
    unittest.main()
