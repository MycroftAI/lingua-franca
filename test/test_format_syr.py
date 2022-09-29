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
from lingua_franca.format import pronounce_number
from lingua_franca.format import date_time_format
from lingua_franca.format import join_list
from lingua_franca.lang.format_syr import get_plural_form_syr
from lingua_franca.time import default_timezone


def setUpModule():
    load_languages(get_supported_langs())
    set_default_lang('syr-sy')

def tearDownModule():
    unload_languages(get_active_langs())


NUMBERS_FIXTURE_EN = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.25: 'ܚܕ ܡܢ ܐܪܒܥܐ',
    0.3: 'ܬܠܬܐ ܡܢ ܥܣܪܐ',
    0.5: 'ܦܠܓܐ',
    0.75: 'ܬܠܬܐ ܡܢ ܐܪܒܥܐ',
    1.333: '1 ܘܚܕ ܡܢ ܬܠܬܐ',
    2.666: '2 ܘܬܪܝܢ ܡܢ ܬܠܬܐ',
    1.25: '1 ܘܚܕ ܡܢ ܐܪܒܥܐ',
    1.75: '1 ܘܬܠܬܐ ܡܢ ܐܪܒܥܐ',
    3.4: '3 ܘܬܪܝܢ ܡܢ ܚܡܫܐ',
    16.8333: '16 ܘܚܡܫܐ ܡܢ ܫܬܐ',
    12.5714: '12 ܘܐܪܒܥܐ ܡܢ ܫܒܥܐ',
    9.625: '9 ܘܚܡܫܐ ܡܢ ܬܡܢܝܐ',
    6.777: '6 ܘܫܒܥܐ ܡܢ ܬܫܥܐ',
    3.1: '3 ܘܚܕ ܡܢ ܥܣܪܐ',
    2.272: '2 ܘܬܠܬܐ ܡܢ ܚܕܥܣܪ',
    5.583: '5 ܘܫܒܥܐ ܡܢ ܬܪܥܣܪ',
    8.384: '8 ܘܚܡܫܐ ܡܢ ܬܠܬܥܣܪ',
    0.071: 'ܚܕ ܡܢ ܐܪܒܥܣܪ',
    6.466: '6 ܘܫܒܥܐ ܡܢ ܚܡܫܥܣܪ',
    8.312: '8 ܘܚܡܫܐ ܡܢ ܫܬܥܣܪ',
    2.176: '2 ܘܬܠܬܐ ܡܢ ܫܒܥܣܪ',
    200.722: '200 ܘܬܠܬܥܣܪ ܡܢ ܬܡܢܥܣܪ',
    7.421: '7 ܘܬܡܢܝܐ ܡܢ ܬܫܥܣܪ',
    0.05: 'ܚܕ ܡܢ ܥܣܪܝܢ'
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
                         '5 ܘܦܠܓܐ',
                         'should format 5.5 as 5 and a half not {}'.format(
                             nice_number(5.5, denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, denominators=[1, 2]),
                         '2.333',
                         'should format 2.333 as 2.333 not {}'.format(
                             nice_number(2.333, denominators=[1, 2])))

    def test_no_speech(self):
        self.assertEqual(nice_number(12.421, speech=False),
                         '12 8/19',
                         'should format 12.421 as 12 8/19 not {}'.format(
                             nice_number(12.421, speech=False)))
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
        self.assertEqual(pronounce_number(-15), "ܣܚܘܦܐ ܚܡܫܥܣܪ")
        self.assertEqual(pronounce_number(-20), "ܣܚܘܦܐ ܥܣܪܝܢ")
        self.assertEqual(pronounce_number(-27), "ܣܚܘܦܐ ܥܣܪܝܢ ܘܫܒܥܐ")
    
    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "ܚܡܫܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(-0.05), "ܣܚܘܦܐ ܚܡܫܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(1.234),
                         "ܚܕ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(21.234),
                         "ܥܣܪܝܢ ܘܚܕ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "ܥܣܪܝܢ ܘܚܕ ܘܬܪܝܢ ܡܢ ܥܣܪܐ")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "ܥܣܪܝܢ ܘܚܕ")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "ܥܣܪܝܢ ܘܚܕ ܘܬܪܝܢܡܐܐ ܘܬܠܬܝܢ ܘܐܪܒܥܐ ܡܢ ܐܠܦܐ")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "ܥܣܪܝܢ ܘܚܕ ܘܬܪܝܢܡܐܐ ܘܬܠܬܝܢ ܘܐܪܒܥܐ ܡܢ ܐܠܦܐ")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "ܥܣܪܝܢ ܘܚܕ ܘܬܪܝܢܡܐܐ ܘܬܠܬܝܢ ܘܐܪܒܥܐ ܡܢ ܐܠܦܐ")
        self.assertEqual(pronounce_number(-1.234),
                         "ܣܚܘܦܐ ܚܕ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(-21.234),
                         "ܣܚܘܦܐ ܥܣܪܝܢ ܘܚܕ ܘܥܣܪܝܢ ܘܬܠܬܐ ܡܢ ܡܐܐ")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "ܣܚܘܦܐ ܥܣܪܝܢ ܘܚܕ ܘܬܪܝܢ ܡܢ ܥܣܪܐ")

    def test_convert_hundreds(self):
        self.assertEqual(pronounce_number(100), "ܡܐܐ")
        self.assertEqual(pronounce_number(666), "ܫܬܡܐܐ ܘܫܬܝܢ ܘܫܬܐ")
        self.assertEqual(pronounce_number(1456), "ܐܠܦܐ ܘܐܪܒܥܡܐܐ ܘܚܡܫܝܢ ܘܫܬܐ")
        self.assertEqual(pronounce_number(1567), "ܐܠܦܐ ܘܚܡܫܡܐܐ ܘܫܬܝܢ ܘܫܒܥܐ")
        self.assertEqual(pronounce_number(3456), "ܬܠܬܐ ܐܠܦܐ ܘܐܪܒܥܡܐܐ ܘܚܡܫܝܢ ܘܫܬܐ")
        self.assertEqual(pronounce_number(18691), "ܬܡܢܥܣܪ ܐܠܦܐ ܘܫܬܡܐܐ ܘܬܫܥܝܢ ܘܚܕ")
        self.assertEqual(pronounce_number(103254654), 
        "ܡܐܐ ܘܬܠܬܐ ܡܠܝܘܢܐ ܘܬܪܝܢܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ ܐܠܦܐ ܘܫܬܡܐܐ ܘܚܡܫܝܢ ܘܐܪܒܥܐ")
        self.assertEqual(pronounce_number(1512457), "ܚܕ ܡܠܝܘܢܐ ܘܚܡܫܡܐܐ ܘܬܪܥܣܪ ܐܠܦܐ ܘܐܪܒܥܡܐܐ ܘܚܡܫܝܢ ܘܫܒܥܐ")
        self.assertEqual(pronounce_number(209996), "ܬܪܝܢܡܐܐ ܘܬܫܥܐ ܐܠܦܐ ܘܬܫܥܡܐܐ ܘܬܫܥܝܢ ܘܫܬܐ")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "ܣܝܦܪ")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "ܬܠܬܐ ܘܬܠܬܐ ܡܢ ܥܣܪܐ ܥܦܝܦ ܥܣܪܐ ܒܚܝܠܐ ܕܚܕ")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "ܬܪܝܢ ܘܬܫܥܝܢ ܘܬܫܥܐ ܡܢ ܡܐܐ ܥܦܝܦ ܥܣܪܐ ܒܚܝܠܐ ܕܬܡܢܝܐ")        

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "ܩܕܡܝܐ")
        self.assertEqual(pronounce_number(10, ordinals=True), "ܥܣܝܪܝܐ")
        self.assertEqual(pronounce_number(15, ordinals=True), "ܚܡܫܥܣܝܪܝܐ")
        self.assertEqual(pronounce_number(20, ordinals=True), "ܥܣܪܝܢܝܐ")
        self.assertEqual(pronounce_number(27, ordinals=True), "ܥܣܪܝܢ ܘܫܒܝܥܝܐ")
        self.assertEqual(pronounce_number(30, ordinals=True), "ܬܠܬܝܢܝܐ")
        self.assertEqual(pronounce_number(33, ordinals=True), "ܬܠܬܝܢ ܘܬܠܝܬܝܐ")
        self.assertEqual(pronounce_number(55, ordinals=True), "ܚܡܫܝܢ ܘܚܡܝܫܝܐ")
        self.assertEqual(pronounce_number(100, ordinals=True), "ܐܡܝܐ")
        self.assertEqual(pronounce_number(1000, ordinals=True), "ܐܠܦܝܐ")
        self.assertEqual(pronounce_number(1500, ordinals=True), "ܐܠܦܐ ܘܚܡܫܡܝܐ")
        self.assertEqual(pronounce_number(10000, ordinals=True), "ܪܒܘܬܢܝܐ")      


# def nice_time(dt, lang="syr-sy", speech=True, use_24hour=False,
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
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, "syr-sy", True, False, False))

        self.assertEqual(nice_time(dt),
                         "ܚܕ ܘܥܣܪܝܢ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܚܕ ܘܥܣܪܝܢ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ ܒܬܪ ܛܗܪܐ")
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
                         "ܬܠܬܥܣܪ ܘܥܣܪܝܢ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ܬܠܬܥܣܪ ܘܥܣܪܝܢ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ܚܕ")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܚܕ ܒܬܪ ܛܗܪܐ")
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
                         "ܬܠܬܥܣܪ")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ܬܠܬܥܣܪ")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ܚܕ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܚܕ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ ܒܬܪ ܛܗܪܐ")
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
                         "ܬܠܬܥܣܪ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ܬܠܬܥܣܪ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ܬܪܥܣܪ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܬܪܥܣܪ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ ܩܕܡ ܛܗܪܐ")
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
                         "ܣܝܦܪ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ܣܝܦܪ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ܚܕ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܚܕ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ ܩܕܡ ܛܗܪܐ")
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
                         "ܚܕ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ܚܕ ܘܬܪܝܢ ܩܛܝܢܬ̈ܐ")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ܬܪܥܣܪ ܘܪܘܒܥܐ")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܬܪܥܣܪ ܘܪܘܒܥܐ ܒܬܪ ܛܗܪܐ")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ܚܡܫܐ ܘܦܠܓܐ ܩܕܡ ܛܗܪܐ")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ܪܘܒܥܐ ܩܐ ܬܪܝܢ")

    def test_join(self):
        self.assertEqual(join_list(None, "and"), "")
        self.assertEqual(join_list([], "and"), "")

        self.assertEqual(join_list(["ܐ"], "ܘ"), "ܐ")
        self.assertEqual(join_list(["ܐ", "ܒ"], "ܘ"), "ܐ ܘ ܒ")
        self.assertEqual(join_list(["ܐ", "ܒ"], "ܐܘ"), "ܐ ܐܘ ܒ")

        self.assertEqual(join_list(["ܐ", "ܒ", "ܓ"], "ܘ"), "ܐ, ܒ ܘ ܓ")
        self.assertEqual(join_list(["ܐ", "ܒ", "ܓ"], "ܐܘ"), "ܐ, ܒ ܐܘ ܓ")
        self.assertEqual(join_list(["ܐ", "ܒ", "ܓ"], "ܐܘ", "؛"), "ܐ؛ ܒ ܐܘ ܓ")
        self.assertEqual(join_list(["ܐ", "ܒ", "ܓ", "ܕ"], "ܐܘ"), "ܐ, ܒ, ܓ ܐܘ ܕ")

        self.assertEqual(join_list([1, "ܒ", 3, "ܕ"], "ܐܘ"), "1, ܒ, 3 ܐܘ ܕ")

class TestPluralForms(unittest.TestCase):
    def test_pluralize(self):
        self.assertEqual(get_plural_form_syr("ܫܪܪܐ", 1), "ܫܪܪܐ")
        self.assertEqual(get_plural_form_syr("ܫܪܪܐ", 2), "ܫܪܪ̈ܐ") # Pluralize
        self.assertEqual(get_plural_form_syr("ܫܪܪܬܐ", 1), "ܫܪܪܬܐ")
        self.assertEqual(get_plural_form_syr("ܫܪܪܬܐ", 2), "ܫܪܪ̈ܬܐ") # Pluralize
        self.assertEqual(get_plural_form_syr("ܒܝܬܐ", 1), "ܒܝܬܐ")
        self.assertEqual(get_plural_form_syr("ܒܝܬܐ", 2), "ܒܝܬ̈ܐ") # Pluralize
        self.assertEqual(get_plural_form_syr("ܝܠܘܦܐ", 2), "ܝܠܘܦ̈ܐ") # Pluralize        
        self.assertEqual(get_plural_form_syr("ܟܠܒܐ", 2), "ܟܠܒ̈ܐ") # Pluralize

        self.assertEqual(get_plural_form_syr("ܒܝܬ̈ܐ", 1), "ܒܝܬܐ") # Singularize
        self.assertEqual(get_plural_form_syr("ܚܒܘܫ̈ܐ", 1), "ܚܒܘܫܐ") # Singularize
        self.assertEqual(get_plural_form_syr("ܦܬܘܪ̈ܐ", 1), "ܦܬܘܪܐ") # Singularize


if __name__ == "__main__":
    unittest.main()
