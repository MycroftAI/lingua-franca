#
# Copyright 2021 Mycroft AI Inc.
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
# See the License for the specific language governing permissions və
# limitations under the License.
#
import json
import unittest
import datetime
import ast
import warnings
import sys
from pathlib import Path

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
from lingua_franca.time import default_timezone


def setUpModule():
    load_languages(get_supported_langs())
    # TODO spin English tests off into another file, like other languages, so we
    # don't have to do this confusing thing in the "master" test_format.py
    set_default_lang('az-az')


def tearDownModule():
    unload_languages(get_active_langs())


NUMBERS_FIXTURE_AZ = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: 'yarım',
    1.333: '1 və üçdə 1',
    2.666: '2 və üçdə 2',
    0.25: 'dörddə 1',
    1.25: '1 və dörddə 1',
    0.75: 'dörddə 3',
    1.75: '1 və dörddə 3',
    3.4: '3 və beşdə 2',
    16.8333: '16 və altıda 5',
    12.5714: '12 və yeddidə 4',
    9.625: '9 və səkkizdə 5',
    6.777: '6 və doqquzda 7',
    3.1: '3 və onda 1',
    2.272: '2 və on birdə 3',
    5.583: '5 və on ikidə 7',
    8.384: '8 və on üçdə 5',
    0.071: 'on dörddə 1',
    6.466: '6 və on beşdə 7',
    8.312: '8 və on altıda 5',
    2.176: '2 və on yeddidə 3',
    200.722: '200 və on səkkizdə 13',
    7.421: '7 və on doqquzda 8',
    0.05: 'iyirmidə 1'
}


class TestNiceNumberFormat(unittest.TestCase):

    tmp_var = None

    def set_tmp_var(self, val):
        self.tmp_var = val

    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_AZ.items():
            self.assertEqual(nice_number(number), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(number)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, denominators=[1, 2, 3]),
                         '5 yarım',
                         'should format 5.5 as 5 yarım not {}'.format(
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

    def test_unknown_language(self):
        """ An unknown / unhandled language should return the string
            representation of the input number.
        """
        def bypass_warning():
            self.assertEqual(
                nice_number(5.5, lang='as-df'), '5.5',
                'should format 5.5 '
                'as 5.5 not {}'.format(
                    nice_number(5.5, lang='as-df')))

        # Should throw a warning. Would raise the same text as a
        # NotImplementedError, but nice_number() bypasses and returns
        # its input as a string
        self.assertWarns(UserWarning, bypass_warning)


class TestPronounceNumber(unittest.TestCase):
    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "sıfır")
        self.assertEqual(pronounce_number(1), "bir")
        self.assertEqual(pronounce_number(10), "on")
        self.assertEqual(pronounce_number(15), "on beş")
        self.assertEqual(pronounce_number(20), "iyirmi")
        self.assertEqual(pronounce_number(27), "iyirmi yeddi")
        self.assertEqual(pronounce_number(30), "otuz")
        self.assertEqual(pronounce_number(33), "otuz üç")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "mənfi bir")
        self.assertEqual(pronounce_number(-10), "mənfi on")
        self.assertEqual(pronounce_number(-15), "mənfi on beş")
        self.assertEqual(pronounce_number(-20), "mənfi iyirmi")
        self.assertEqual(pronounce_number(-27), "mənfi iyirmi yeddi")
        self.assertEqual(pronounce_number(-30), "mənfi otuz")
        self.assertEqual(pronounce_number(-33), "mənfi otuz üç")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "sıfır nöqtə sıfır beş")
        self.assertEqual(pronounce_number(-0.05), "mənfi sıfır nöqtə sıfır beş")
        self.assertEqual(pronounce_number(1.234),
                         "bir nöqtə iki üç")
        self.assertEqual(pronounce_number(21.234),
                         "iyirmi bir nöqtə iki üç")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "iyirmi bir nöqtə iki")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "iyirmi bir")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "iyirmi bir nöqtə iki üç dörd")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "iyirmi bir nöqtə iki üç dörd")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "iyirmi bir nöqtə iki üç dörd")
        self.assertEqual(pronounce_number(-1.234),
                         "mənfi bir nöqtə iki üç")
        self.assertEqual(pronounce_number(-21.234),
                         "mənfi iyirmi bir nöqtə iki üç")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "mənfi iyirmi bir nöqtə iki")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "mənfi iyirmi bir")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "mənfi iyirmi bir nöqtə iki üç dörd")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "mənfi iyirmi bir nöqtə iki üç dörd")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "mənfi iyirmi bir nöqtə iki üç dörd")

    def test_convert_hundreds(self):
        self.assertEqual(pronounce_number(100), "yüz")
        self.assertEqual(pronounce_number(666), "altı yüz altmış altı")
        self.assertEqual(pronounce_number(1456), "min, dörd yüz əlli altı")
        self.assertEqual(pronounce_number(103254654), "yüz üç milyon, "
                                                      "iki yüz əlli dörd min, "
                                                      "altı yüz əlli dörd")
        self.assertEqual(pronounce_number(1512457), "bir milyon, "
                                                    "beş yüz on iki min, "
                                                    "dörd yüz əlli yeddi")
        self.assertEqual(pronounce_number(209996), "iki yüz doqquz min, "
                                                   "doqquz yüz doxsan altı")





    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "sıfır")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "üç nöqtə üç vurulsun on üstü bir")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "iki nöqtə doqquz doqquz vurulsun on üstü səkkiz")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "iki nöqtə doqquz doqquz yeddi doqquz iki beş vurulsun "
                         "on üstü səkkiz")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "bir nöqtə altı yeddi iki vurulsun on üstü "
                         "mənfi iyirmi yeddi")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "bir nöqtə bir vurulsun "
                                        "on üstü mənfi yüz əlli")

    def test_large_numbers(self):
        self.assertEqual(
            pronounce_number(299792458, short_scale=True),
            "iki yüz doxsan doqquz milyon, yeddi yüz "
            "doxsan iki min, dörd yüz əlli səkkiz")
        self.assertEqual(
            pronounce_number(299792458, short_scale=False),
            "iki yüz doxsan doqquz milyon, yeddi yüz "
            "doxsan iki min, dörd yüz əlli səkkiz")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=True),
            "yüz kvintilyon, otuz dörd kvadrilyon, "
            "iki yüz doxsan doqquz milyon, yeddi yüz "
            "doxsan iki min, dörd yüz əlli səkkiz")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=False),
            "yüz trilyon, otuz dörd min milyard, "
            "iki yüz doxsan doqquz milyon, yeddi yüz "
            "doxsan iki min, dörd yüz əlli səkkiz")
        self.assertEqual(
            pronounce_number(10000000000, short_scale=True),
            "on milyard")
        self.assertEqual(
            pronounce_number(1000000000000, short_scale=True),
            "bir trilyon")
        self.assertEqual(
            pronounce_number(1000001, short_scale=True),
            "bir milyon, bir")
        self.assertEqual(pronounce_number(95505896639631893),
                         "doxsan beş kvadrilyon, beş yüz beş trilyon, "
                         "səkkiz yüz doxsan altı milyard, "
                         "altı yüz otuz doqquz milyon, "
                         "altı yüz otuz bir min, səkkiz yüz doxsan üç")
        self.assertEqual(pronounce_number(95505896639631893,
                                          short_scale=False),
                         "doxsan beş min beş yüz beş milyard, "
                         "səkkiz yüz doxsan altı min altı yüz "
                         "otuz doqquz milyon, altı yüz otuz bir min, "
                         "səkkiz yüz doxsan üç")
        self.assertEqual(pronounce_number(10e32, places=1),
                         "bir dekilyon")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "sonsuzluq")
        self.assertEqual(
            pronounce_number(float("inf")),
            "sonsuzluq")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "mənfi sonsuzluq")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "birinci")
        self.assertEqual(pronounce_number(10, ordinals=True), "onuncu")
        self.assertEqual(pronounce_number(15, ordinals=True), "on beşinci")
        self.assertEqual(pronounce_number(20, ordinals=True), "iyirminci")
        self.assertEqual(pronounce_number(27, ordinals=True), "iyirmi yeddinci")
        self.assertEqual(pronounce_number(30, ordinals=True), "otuzuncu")
        self.assertEqual(pronounce_number(33, ordinals=True), "otuz üçüncü")
        self.assertEqual(pronounce_number(100, ordinals=True), "yüzüncü")
        self.assertEqual(pronounce_number(1000, ordinals=True), "mininci")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "on mininci")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "on səkkiz min, altı yüz doxsan birinci")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "min, beş yüz altmış yeddinci")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "bir nöqtə altı yeddi iki vurulsun on üstü mənfi "
                         "iyirmi yeddinci")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "on səkkiz milyonuncu")
        self.assertEqual(pronounce_number(18e12, ordinals=True,
                                          short_scale=False),
                         "on səkkiz milyardıncı")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "on səkkiz trilyonuncu")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "on səkkiz "
                                                              "trilyonuncu")


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
                         nice_time(dt, "az-az", True, False, False))

        self.assertEqual(nice_time(dt),
                         "ikiyə iyirmi iki dəqiqə işləyib")

        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gündüz ikiyə iyirmi iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "gündüz 1:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "on üç iyirmi iki")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "on üç iyirmi iki")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "bir tamamdır")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gündüz bir tamamdır")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "gündüz 1:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "on üç sıfır sıfır")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "on üç sıfır sıfır")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gündüz ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "gündüz 1:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "on üç sıfır iki")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "on üç sıfır iki")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "birə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gecə birə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, speech=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "gecə 12:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "sıfır sıfır sıfır iki")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "sıfır sıfır sıfır iki")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gecə ikiyə iki dəqiqə işləyib")
        self.assertEqual(nice_time(dt, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_ampm=True),
                         "gecə 1:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "sıfır bir sıfır iki")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "sıfır bir sıfır iki")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "birə on beş dəqiqə işləyib")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gündüz birə on beş dəqiqə işləyib")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "gecə altının yarısı")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ikiyə on beş dəqiqə qalıb")

    def test_nice_date(self):
        lang = "az-az"
        i = 1
        while (self.test_config[lang].get('test_nice_date') and
                self.test_config[lang]['test_nice_date'].get(str(i))):
            p = self.test_config[lang]['test_nice_date'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5])
            print('Testing for ' + lang + ' that ' + str(dt) +
                    ' is date ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'],
                                nice_date(dt, lang=lang, now=now))
            i = i + 1

        for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3) +
                    datetime.timedelta(n) for n in range(368)):
            self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        # TODO: migrate these tests (in res files) to respect the new
        # language loading features. Right now, some of them break if
        # their languages are not default.
        lang = "az-az"
        set_default_lang(lang)
        i = 1
        while (self.test_config[lang].get('test_nice_date_time') and
                self.test_config[lang]['test_nice_date_time'].get(str(i))):
            p = self.test_config[lang]['test_nice_date_time'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            np = ast.literal_eval(p['now'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5],
                tzinfo=default_timezone())
            now = None if not np else datetime.datetime(
                np[0], np[1], np[2], np[3], np[4], np[5],
                tzinfo=default_timezone())
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
        lang = "az-az"
        i = 1
        while (self.test_config[lang].get('test_nice_year') and
                self.test_config[lang]['test_nice_year'].get(str(i))):
            p = self.test_config[lang]['test_nice_year'][str(i)]
            dp = ast.literal_eval(p['datetime_param'])
            dt = datetime.datetime(
                dp[0], dp[1], dp[2], dp[3], dp[4], dp[5])
            print('Testing for ' + lang + ' that ' + str(dt) +
                    ' is year ' + p['assertEqual'])
            self.assertEqual(p['assertEqual'], nice_year(
                dt, lang=lang, bc=ast.literal_eval(p['bc'])))
            i = i + 1

        # Test all years from 0 to 9999 for az,
        # that some output is produced
        print("Test all years in " + lang)
        for i in range(1, 9999):
            dt = datetime.datetime(i, 1, 31, 13, 2, 3, tzinfo=default_timezone())
            self.assertTrue(len(nice_year(dt, lang=lang)) > 0)

    def test_nice_duration(self):
        self.assertEqual(nice_duration(1), "bir saniyə")
        self.assertEqual(nice_duration(3), "üç saniyə")
        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "bir dəqiqə bir saniyə")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "bir saat iyirmi üç dəqiqə iyirmi saniyə")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "on üç saat əlli üç dəqiqə iyirmi saniyə")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "beş gün on səkkiz saat əlli üç dəqiqə iyirmi saniyə")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5g 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5g 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "və"), "")
        self.assertEqual(join_list([], "və"), "")

        self.assertEqual(join_list(["a"], "və"), "a")
        self.assertEqual(join_list(["a", "b"], "və"), "a və b")
        self.assertEqual(join_list(["a", "b"], "ya"), "a ya b")

        self.assertEqual(join_list(["a", "b", "c"], "və"), "a, b və c")
        self.assertEqual(join_list(["a", "b", "c"], "ya"), "a, b ya c")
        self.assertEqual(join_list(["a", "b", "c"], "ya", ";"), "a; b ya c")
        self.assertEqual(join_list(["a", "b", "c", "d"], "ya"), "a, b, c ya d")

        self.assertEqual(join_list([1, "b", 3, "d"], "ya"), "1, b, 3 ya d")


if __name__ == "__main__":
    unittest.main()
