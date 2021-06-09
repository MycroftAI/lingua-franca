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

from lingua_franca import get_default_lang, set_default_lang
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


NUMBERS_FIXTURE_SL = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: '1 polovica',
    1.333: '1 in 1 tretjina',
    2.666: '2 in 2 tretjini',
    0.25: '1 četrtina',
    1.25: '1 in 1 četrtina',
    0.75: '3 četrtine',
    1.75: '1 in 3 četrtine',
    3.4: '3 in 2 petini',
    16.8333: '16 in 5 šestin',
    12.5714: '12 in 4 sedmine',
    9.625: '9 in 5 osmin',
    6.777: '6 in 7 devetin',
    3.1: '3 in 1 desetina',
    2.272: '2 in 3 enajstine',
    5.583: '5 in 7 dvanajstin',
    8.384: '8 in 5 trinajstin',
    0.071: '1 štirinajstina',
    6.466: '6 in 7 petnajstin',
    8.312: '8 in 5 šestnajstin',
    2.176: '2 in 3 sedemnajstine',
    200.722: '200 in 13 osemnajstin',
    7.421: '7 in 8 devetnajstin',
    0.05: '1 dvajsetina'
}


class TestNiceNumberFormat(unittest.TestCase):
    def setUp(self):
        self.old_lang = get_default_lang()
        set_default_lang("sl-si")

    def tearDown(self):
        if self.old_lang:
            set_default_lang(self.old_lang)

    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_SL.items():
            self.assertEqual(nice_number(number), number_str,
                             'should format {} as {} and not {}'.format(
                                 number, number_str, nice_number(number)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, denominators=[1, 2, 3]),
                         '5 in 1 polovica',
                         'should format 5.5 as 5 in 1 polovica not {}'.format(
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
    def setUp(self):
        self.old_lang = get_default_lang()
        set_default_lang("sl-si")

    def tearDown(self):
        if self.old_lang:
            set_default_lang(self.old_lang)

    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "nič")
        self.assertEqual(pronounce_number(1), "ena")
        self.assertEqual(pronounce_number(10), "deset")
        self.assertEqual(pronounce_number(15), "petnajst")
        self.assertEqual(pronounce_number(20), "dvajset")
        self.assertEqual(pronounce_number(27), "sedemindvajset")
        self.assertEqual(pronounce_number(30), "trideset")
        self.assertEqual(pronounce_number(33), "triintrideset")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "minus ena")
        self.assertEqual(pronounce_number(-10), "minus deset")
        self.assertEqual(pronounce_number(-15), "minus petnajst")
        self.assertEqual(pronounce_number(-20), "minus dvajset")
        self.assertEqual(pronounce_number(-27), "minus sedemindvajset")
        self.assertEqual(pronounce_number(-30), "minus trideset")
        self.assertEqual(pronounce_number(-33), "minus triintrideset")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "nič celih nič pet")
        self.assertEqual(pronounce_number(-0.05), "minus nič celih nič pet")
        self.assertEqual(pronounce_number(1.234),
                         "ena cela dve tri")
        self.assertEqual(pronounce_number(21.234),
                         "enaindvajset celih dve tri")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "enaindvajset celih dve")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "enaindvajset")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "enaindvajset celih dve tri štiri")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "enaindvajset celih dve tri štiri")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "enaindvajset celih dve tri štiri")
        self.assertEqual(pronounce_number(-1.234),
                         "minus ena cela dve tri")
        self.assertEqual(pronounce_number(-21.234),
                         "minus enaindvajset celih dve tri")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "minus enaindvajset celih dve")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "minus enaindvajset")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "minus enaindvajset celih dve tri štiri")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "minus enaindvajset celih dve tri štiri")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "minus enaindvajset celih dve tri štiri")

    def test_convert_hundreds(self):
        self.assertEqual(pronounce_number(100), "sto")
        self.assertEqual(pronounce_number(666), "šeststo šestinšestdeset")
        self.assertEqual(pronounce_number(
            1456), "tisoč štiristo šestinpetdeset")
        self.assertEqual(pronounce_number(103254654), "sto trije milijoni "
                                                      "dvesto štiriinpetdeset "
                                                      "tisoč šeststo "
                                                      "štiriinpetdeset")
        self.assertEqual(pronounce_number(1512457), "milijon petsto dvanajst"
                                                    " tisoč štiristo "
                                                    "sedeminpetdeset")
        self.assertEqual(pronounce_number(209996), "dvesto devet tisoč "
                                                   "devetsto šestindevetdeset")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "nič")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "tri cele tri krat deset na ena")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "dve celi devet devet krat deset na osem")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "dve celi devet devet sedem devet dve pet "
                         "krat deset na osem")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "ena cela šest sedem dve krat deset na "
                         "minus sedemindvajset")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "ena cela ena krat deset na "
                                        "minus sto petdeset")
        # value is platform dependent so better not use in tests?
        # self.assertEqual(
        #    pronounce_number(sys.float_info.min), "dve celi dve dve krat "
        #                                          "deset na minus tristo osem")
        # self.assertEqual(
        #    pronounce_number(sys.float_info.max), "ena cela sedem devet krat "
        #                                          "deset na tristo osem")

    def test_large_numbers(self):
        self.assertEqual(
            pronounce_number(299792458, short_scale=True),
            "dvesto devetindevetdeset milijonov sedemsto "
            "dvaindevetdeset tisoč štiristo oseminpetdeset")
        self.assertEqual(
            pronounce_number(299792458, short_scale=False),
            "dvesto devetindevetdeset milijonov sedemsto "
            "dvaindevetdeset tisoč štiristo oseminpetdeset")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=True),
            "sto kvintilijonov štiriintrideset kvadrilijonov "
            "dvesto devetindevetdeset milijonov sedemsto "
            "dvaindevetdeset tisoč štiristo oseminpetdeset")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=False),
            "sto trilijonov štiriintrideset bilijard "
            "dvesto devetindevetdeset milijonov sedemsto "
            "dvaindevetdeset tisoč štiristo oseminpetdeset")
        self.assertEqual(
            pronounce_number(10000000000, short_scale=True),
            "deset bilijonov")
        self.assertEqual(
            pronounce_number(1000000000000, short_scale=True),
            "trilijon")
        # TODO maybe beautify this
        self.assertEqual(
            pronounce_number(1000001, short_scale=True),
            "milijon ena")
        self.assertEqual(pronounce_number(95505896639631893),
                         "petindevetdeset kvadrilijonov petsto pet trilijonov "
                         "osemsto šestindevetdeset bilijonov šeststo devetintrideset "
                         "milijonov šeststo enaintrideset tisoč osemsto triindevetdeset")
        self.assertEqual(pronounce_number(95505896639631893,
                                          short_scale=False),
                         "petindevetdeset bilijard osemsto "
                         "šestindevetdeset milijard šeststo enaintrideset "
                         "tisoč osemsto triindevetdeset")
        # TODO floating point rounding issues might happen
        # Automatic switch to scientific notation because such big numbers are not (yet) supported
        self.assertEqual(pronounce_number(1.9874522571e80, places=9),
                         "ena cela devet osem sedem štiri "
                         "pet dve krat deset na osemdeset")
        self.assertEqual(pronounce_number(1.00000000000000001e150),
                         "ena krat deset na sto petdeset")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "neskončno")
        self.assertEqual(
            pronounce_number(float("inf")),
            "neskončno")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "minus neskončno")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "prvi")
        self.assertEqual(pronounce_number(10, ordinals=True), "deseti")
        self.assertEqual(pronounce_number(15, ordinals=True), "petnajsti")
        self.assertEqual(pronounce_number(20, ordinals=True), "dvajseti")
        self.assertEqual(pronounce_number(
            27, ordinals=True), "sedemindvajseti")
        self.assertEqual(pronounce_number(30, ordinals=True), "trideseti")
        self.assertEqual(pronounce_number(33, ordinals=True), "triintrideseti")
        self.assertEqual(pronounce_number(100, ordinals=True), "stoti")
        self.assertEqual(pronounce_number(1000, ordinals=True), "tisoči")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "desettisoči")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "osemnajsttisočšeststoenaindevetdeseti")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "tisočpetstosedeminšestdeseti")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "ena cela šest sedem dve krat "
                         "deset na minus sedemindvajseti")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "osemnajstmilijonti")
        self.assertEqual(pronounce_number(18e12, ordinals=True,
                                          short_scale=False),
                         "osemnajstbilijonti")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "osemnajsttrilijonti")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "osemnajsttrilijonti")


class TestNiceDateFormat(unittest.TestCase):
    def setUp(self):
        self.old_lang = get_default_lang()
        set_default_lang("sl-si")

    def tearDown(self):
        if self.old_lang:
            set_default_lang(self.old_lang)

    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        language = "sl-si"
        config = date_time_format.config_path + "/" + language + "/date_time_test.json"

        cls.test_config = {}
        with open(config, encoding="utf8") as file:
            cls.test_config[language] = json.loads(file.read())

    def test_convert_times(self):
        dt = datetime.datetime(2017, 1, 31,
                               13, 22, 3, tzinfo=default_timezone())

        # Verify defaults haven't changed
        self.assertEqual(nice_time(dt),
                         nice_time(dt, "sl-si", True, False, False))

        self.assertEqual(nice_time(dt),
                         "dvaindvajset čez ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dvaindvajset čez ena p.m.")
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
                         "trinajst dvaindvajset")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trinajst dvaindvajset")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "ena p.m.")
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
                         "trinajst nič nič")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trinajst nič nič")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve čez ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve čez ena p.m.")
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
                         "trinajst nič dve")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "trinajst nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve čez dvanajst")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve čez dvanajst a.m.")
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
                         "nič nič dve")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "nič nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               20, 40, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dvajset do devetih")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dvajset do devetih p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               0, 58, 40, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve do enih")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve do enih a.m.")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "dve čez ena")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "dve čez ena a.m.")
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
                         "ena nič dve")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "ena nič dve")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "petnajst čez dvanajst")
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "petnajst čez dvanajst p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 15, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "petnajst čez ena a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "petnajst do dveh a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_ampm=True),
                         "pol šestih a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt),
                         "petnajst do dveh")

    def test_nice_date(self):
        for lang in self.test_config:
            i = 1
            while (self.test_config[lang].get('test_nice_date') and
                   self.test_config[lang]['test_nice_date'].get(str(i))):
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

    def test_nice_date_time(self):
        for lang in self.test_config:
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
        for lang in self.test_config:
            i = 1
            while (self.test_config[lang].get('test_nice_year') and
                   self.test_config[lang]['test_nice_year'].get(str(i))):
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
        for lang in self.test_config:
            print("Test all years in " + lang)
            for i in range(1, 9999):
                dt = datetime.datetime(i, 1, 31, 13, 2, 3,
                                       tzinfo=default_timezone())
                self.assertTrue(len(nice_year(dt, lang=lang)) > 0)
                # Looking through the date sequence can be helpful

#                print(nice_year(dt, lang=lang))

    def test_nice_duration(self):
        # TODO implement better plural support for nice_duration
        # Correct results are in comments

        self.assertEqual(nice_duration(1), "ena sekunda")
        self.assertEqual(nice_duration(2), "dve sekund")  # dve sekundi
        self.assertEqual(nice_duration(3), "tri sekund")  # tri sekunde
        self.assertEqual(nice_duration(4), "štiri sekund")  # štiri sekunde
        self.assertEqual(nice_duration(5), "pet sekund")
        self.assertEqual(nice_duration(6), "šest sekund")

        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "ena minuta ena sekunda")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "ena ura triindvajset minut dvajset sekund")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "trinajst ur triinpetdeset minut dvajset sekund")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000),
                         "pet dni  osemnajst ur triinpetdeset minut dvajset sekund")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "in"), "")
        self.assertEqual(join_list([], "in"), "")

        self.assertEqual(join_list(["a"], "in"), "a")
        self.assertEqual(join_list(["a", "b"], "in"), "a in b")
        self.assertEqual(join_list(["a", "b"], "ali"), "a ali b")

        self.assertEqual(join_list(["a", "b", "c"], "in"), "a, b in c")
        self.assertEqual(join_list(["a", "b", "c"], "ali"), "a, b ali c")
        self.assertEqual(join_list(["a", "b", "c"], "ali", ";"), "a; b ali c")
        self.assertEqual(
            join_list(["a", "b", "c", "d"], "ali"), "a, b, c ali d")

        self.assertEqual(join_list([1, "b", 3, "d"], "ali"), "1, b, 3 ali d")


if __name__ == "__main__":
    unittest.main()
