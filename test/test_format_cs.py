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
    load_language("cs-cz")
    set_default_lang("cs")


def tearDownModule():
    unload_language("cs")


NUMBERS_FIXTURE_CS = {
    1.435634: '1.436',
    2: '2',
    5.0: '5',
    0.027: '0.027',
    0.5: 'polovina',
    1.333: '1 a třetina',
    2.666: '2 a 2 třetiny',
    0.25: 'čtvrtina',
    1.25: '1 a čtvrtina',
    0.75: '3 čtvrtiny',
    1.75: '1 a 3 čtvrtiny',
    3.4: '3 a 2 pětiny',
    16.8333: '16 a 5 šestin',
    12.5714: '12 a 4 sedminy',
    9.625: '9 a 5 osmin',
    6.777: '6 a 7 devítin',
    3.1: '3 a desetina',
    2.272: '2 a 3 jedenáctiny',
    5.583: '5 a 7 dvanáctin',
    8.384: '8 a 5 třináctin',
    0.071: 'čtrnáctina',
    6.466: '6 a 7 patnáctin',
    8.312: '8 a 5 šestnáctin',
    2.176: '2 a 3 sedmnáctiny',
    200.722: '200 a 13 osmnáctin',
    7.421: '7 a 8 devatenáctin',
    0.05: 'dvacetina'
}


class TestNiceNumberFormat(unittest.TestCase):

    def test_convert_float_to_nice_number(self):
        for number, number_str in NUMBERS_FIXTURE_CS.items():
            self.assertEqual(nice_number(number, speech=True), number_str,
                             'měl by zformátovat {} jako {}, ne {}'.format(
                                 number, number_str, nice_number(number, speech=True)))

    def test_specify_denominator(self):
        self.assertEqual(nice_number(5.5, speech=True, denominators=[1, 2, 3]),
                         '5 a polovina',
                         'měl by zformátovat 5.5 jako 5 a půl, ne {}'.format(
                             nice_number(5.5, speech=True, denominators=[1, 2, 3])))
        self.assertEqual(nice_number(2.333, speech=True, denominators=[1, 2]),
                         '2.333',
                         'měl by zformátovat 2.333 jako 2.333, ne {}'.format(
                             nice_number(2.333, speech=True, denominators=[1, 2])))

    def test_no_speech(self):
        self.assertEqual(nice_number(6.777, speech=False),
                         '6 7/9',
                         'měl by zformátovat 6.777 jako 6 7/9 ne {}'.format(
                             nice_number(6.777, speech=False)))
        self.assertEqual(nice_number(6.0, speech=False),
                         '6',
                         'měl by zformátovat 6.0 jako 6 ne {}'.format(
                             nice_number(6.0, speech=False)))


class TestPronounceNumber(unittest.TestCase):

    def test_convert_int(self):
        self.assertEqual(pronounce_number(0), "nula")
        self.assertEqual(pronounce_number(1), "jedna")
        self.assertEqual(pronounce_number(10), "deset")
        self.assertEqual(pronounce_number(15), "patnáct")
        self.assertEqual(pronounce_number(20), "dvacet")
        self.assertEqual(pronounce_number(27), "dvacet sedm")
        self.assertEqual(pronounce_number(30), "třicet")
        self.assertEqual(pronounce_number(33), "třicet tři")

    def test_convert_negative_int(self):
        self.assertEqual(pronounce_number(-1), "mínus jedna")
        self.assertEqual(pronounce_number(-10), "mínus deset")
        self.assertEqual(pronounce_number(-15), "mínus patnáct")
        self.assertEqual(pronounce_number(-20), "mínus dvacet")
        self.assertEqual(pronounce_number(-27), "mínus dvacet sedm")
        self.assertEqual(pronounce_number(-30), "mínus třicet")
        self.assertEqual(pronounce_number(-33), "mínus třicet tři")

    def test_convert_decimals(self):
        self.assertEqual(pronounce_number(0.05), "nula tečka nula pět")
        self.assertEqual(pronounce_number(-0.05), "mínus nula tečka nula pět")
        self.assertEqual(pronounce_number(1.234),
                         "jedna tečka dva tři")
        self.assertEqual(pronounce_number(21.234),
                         "dvacet jedna tečka dva tři")
        self.assertEqual(pronounce_number(21.234, places=1),
                         "dvacet jedna tečka dva")
        self.assertEqual(pronounce_number(21.234, places=0),
                         "dvacet jedna")
        self.assertEqual(pronounce_number(21.234, places=3),
                         "dvacet jedna tečka dva tři čtyři")
        self.assertEqual(pronounce_number(21.234, places=4),
                         "dvacet jedna tečka dva tři čtyři")
        self.assertEqual(pronounce_number(21.234, places=5),
                         "dvacet jedna tečka dva tři čtyři")
        self.assertEqual(pronounce_number(-1.234),
                         "mínus jedna tečka dva tři")
        self.assertEqual(pronounce_number(-21.234),
                         "mínus dvacet jedna tečka dva tři")
        self.assertEqual(pronounce_number(-21.234, places=1),
                         "mínus dvacet jedna tečka dva")
        self.assertEqual(pronounce_number(-21.234, places=0),
                         "mínus dvacet jedna")
        self.assertEqual(pronounce_number(-21.234, places=3),
                         "mínus dvacet jedna tečka dva tři čtyři")
        self.assertEqual(pronounce_number(-21.234, places=4),
                         "mínus dvacet jedna tečka dva tři čtyři")
        self.assertEqual(pronounce_number(-21.234, places=5),
                         "mínus dvacet jedna tečka dva tři čtyři")

    def test_convert_stos(self):
        self.assertEqual(pronounce_number(100), "jedna sto")
        self.assertEqual(pronounce_number(666), "šest sto a šedesát šest")
        self.assertEqual(pronounce_number(1456), "čtrnáct padesát šest")
        self.assertEqual(pronounce_number(103254654), "jedna sto a tři "
                                                      "million, dva sto "
                                                      "a padesát čtyři "
                                                      "tisíc, šest sto "
                                                      "a padesát čtyři")
        self.assertEqual(pronounce_number(1512457), "jedna million, pět sto"
                                                    " a dvanáct tisíc, "
                                                    "čtyři sto a padesát "
                                                    "sedm")
        self.assertEqual(pronounce_number(209996), "dva sto a devět "
                                                   "tisíc, devět sto "
                                                   "a devadesát šest")

    def test_convert_scientific_notation(self):
        self.assertEqual(pronounce_number(0, scientific=True), "nula")
        self.assertEqual(pronounce_number(33, scientific=True),
                         "tři tečka tři krát deset na mocninu jedna")
        self.assertEqual(pronounce_number(299792458, scientific=True),
                         "dva tečka devět devět krát deset na mocninu osm")
        self.assertEqual(pronounce_number(299792458, places=6,
                                          scientific=True),
                         "dva tečka devět devět sedm devět dva pět krát "
                         "deset na mocninu osm")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True),
                         "jedna tečka šest sedm dva krát deset na mocninu "
                         "záporné dvacet sedm")

    def test_auto_scientific_notation(self):
        self.assertEqual(
            pronounce_number(1.1e-150), "jedna tečka jedna krát deset na "
                                        "mocninu záporné jedna sto "
                                        "a padesát")
        # value is platform dependent so better not use in tests?
        # self.assertEqual(
        #    pronounce_number(sys.float_info.min), "dva tečka dva dva times "
        #                                          "ten na mocninu "
        #                                          "negative tři sto "
        #                                          "a osm")
        # self.assertEqual(
        #    pronounce_number(sys.float_info.max), "jedna tečka sedm devět "
        #                                          "krát deset na mocninu"
        #                                          " tři sto a osm")

    def test_large_numbers(self):
        self.assertEqual(
            pronounce_number(299792458, short_scale=True),
            "dva sto a devadesát devět million, sedm sto "
            "a devadesát dva tisíc, čtyři sto a padesát osm")
        self.assertEqual(
            pronounce_number(299792458, short_scale=False),
            "dva sto a devadesát devět milion, sedm sto "
            "a devadesát dva tisíc, čtyři sto a padesát osm")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=True),
            "jedna sto quintillion, třicet čtyři quadrillion, "
            "dva sto a devadesát devět million, sedm sto "
            "a devadesát dva tisíc, čtyři sto a padesát osm")
        self.assertEqual(
            pronounce_number(100034000000299792458, short_scale=False),
            "jedna sto bilion, třicet čtyři tisíc miliarda,"
            " dva sto a devadesát devět milion, sedm sto"
            " a devadesát dva tisíc, čtyři sto a padesát osm")
        self.assertEqual(
            pronounce_number(10000000000, short_scale=True),
            "deset billion")
        self.assertEqual(
            pronounce_number(1000000000000, short_scale=True),
            "jedna trillion")
        # TODO maybe beautify this
        self.assertEqual(
            pronounce_number(1000001, short_scale=True),
            "jedna million, jedna")
        self.assertEqual(pronounce_number(95505896639631893, short_scale=True),
                         "devadesát pět quadrillion, pět sto a pět "
                         "trillion, osm sto a devadesát šest billion, šest "
                         "sto a třicet devět million, šest sto a "
                         "třicet jedna tisíc, osm sto a devadesát tři")
        self.assertEqual(pronounce_number(95505896639631893,
                                          short_scale=False),
                         "devadesát pět tisíc pět sto a pět miliarda, "
                         "osm sto a devadesát šest tisíc šest sto "
                         "a třicet devět milion, šest sto a třicet jedna "
                         "tisíc, osm sto a devadesát tři")
        self.assertEqual(pronounce_number(10e80, places=1),
                         "jedna qesvigintillion")
        # TODO floating point rounding issues might happen
        self.maxDiff = None
        self.assertEqual(pronounce_number(1.9874522571e80, places=9),
                         "jedna sto a devadesát osm quinquavigintillion, "
                         "sedm sto a čtyřicet pět quattuorvigintillion, "
                         "dva sto a dvacet pět tresvigintillion, "
                         "sedm sto a devět uuovigintillion, "
                         "devět sto a devadesát devět unvigintillion, "
                         "devět sto a osmdesát devět vigintillion, "
                         "sedm sto a třicet novemdecillion, devět "
                         "sto a devatenáct octodecillion, devět sto "
                         "a devadesát devět septendecillion, devět sto "
                         "a padesát pět sexdecillion, čtyři sto a "
                         "devadesát osm quindecillion, dva sto a "
                         "čtrnáct quadrdecillion, osm sto a "
                         "čtyřicet pět tredecillion, čtyři sto a "
                         "dvacet devět duodecillion, čtyři sto a "
                         "čtyřicet čtyři undecillion, tři sto a "
                         "třicet šest decillion, sedm sto a dvacet "
                         "čtyři nonillion, pět sto a šedesát devět "
                         "octillion, tři sto a sedmdesát pět "
                         "septillion, dva sto a třicet devět sextillion,"
                         " šest sto a sedmdesát quintillion, pět sto "
                         "a sedmdesát čtyři quadrillion, sedm sto a "
                         "třicet devět trillion, sedm sto a čtyřicet"
                         " osm billion, čtyři sto a sedmdesát million, "
                         "devět sto a patnáct tisíc, sedmdesát dva")
        self.assertEqual(pronounce_number(1.00000000000000001e150),
                         "devět sto a devadesát devět millinillion, devět "
                         "sto a devadesát devět uncentillion, devět sto "
                         "a devadesát devět centillion, devět sto a devadesát"
                         " devět nonagintillion, devět sto a devadesát devět"
                         " octogintillion, devět sto a osmdesát"
                         " septuagintillion, osm sto a třicet pět "
                         "sexagintillion, pět sto a devadesát šest "
                         "quinquagintillion, jedna sto a sedmdesát dva"
                         " quadragintillion, čtyři sto a třicet sedm"
                         " noventrigintillion, tři sto a sedmdesát čtyři"
                         " octotrigintillion, pět sto a devadesát"
                         " septentrigintillion, pět sto a sedmdesát"
                         " tři sestrigintillion, jedna sto a dvacet "
                         "quinquatrigintillion, čtrnáct quattuortrigintillion"
                         ", třicet trestrigintillion, tři sto a "
                         "osmnáct duotrigintillion, sedm sto a devadesát"
                         " tři untrigintillion, devadesát jedna trigintillion,"
                         " jedna sto a šedesát čtyři novemvigintillion, osm"
                         " sto a deset octovigintillion, jedna sto a"
                         " padesát čtyři septemvigintillion, jedna sto "
                         "qesvigintillion, jedna sto a dvanáct "
                         "quinquavigintillion, dva sto a tři "
                         "quattuorvigintillion, šest sto a sedmdesát "
                         "osm tresvigintillion, pět sto a osmdesát "
                         "dva uuovigintillion, devět sto a sedmdesát šest"
                         " unvigintillion, dva sto a devadesát osm "
                         "vigintillion, dva sto a šedesát osm "
                         "novemdecillion, šest sto a šestnáct "
                         "octodecillion, dva sto a dvacet jedna "
                         "septendecillion, jedna sto a padesát jedna"
                         " sexdecillion, devět sto a šedesát dva "
                         "quindecillion, sedm sto a dva"
                         " quadrdecillion, šedesát tredecillion, dva sto"
                         " a šedesát šest duodecillion, jedna sto a "
                         "sedmdesát šest undecillion, pět decillion, čtyři "
                         "sto a čtyřicet nonillion, pět sto a"
                         " šedesát sedm octillion, třicet dva septillion, "
                         "tři sto a třicet jedna sextillion, "
                         "dva sto a osm quintillion, čtyři sto a "
                         "tři quadrillion, devět sto a čtyřicet osm "
                         "trillion, dva sto a třicet tři billion, "
                         "tři sto a sedmdesát tři million, pět "
                         "sto a patnáct tisíc, sedm sto a "
                         "sedmdesát šest")

        # infinity
        self.assertEqual(
            pronounce_number(sys.float_info.max * 2), "nekonečno")
        self.assertEqual(
            pronounce_number(float("inf")),
            "nekonečno")
        self.assertEqual(
            pronounce_number(float("-inf")),
            "záporné nekonečno")

    def test_ordinals(self):
        self.assertEqual(pronounce_number(1, ordinals=True), "první")
        self.assertEqual(pronounce_number(10, ordinals=True), "desátý")
        self.assertEqual(pronounce_number(15, ordinals=True), "patnáctý")
        self.assertEqual(pronounce_number(20, ordinals=True), "dvacátý")
        self.assertEqual(pronounce_number(27, ordinals=True), "dvacet sedmý")
        self.assertEqual(pronounce_number(30, ordinals=True), "třicátý")
        self.assertEqual(pronounce_number(33, ordinals=True), "třicet třetí")
        self.assertEqual(pronounce_number(100, ordinals=True), "stý")
        self.assertEqual(pronounce_number(1000, ordinals=True), "tisící")
        self.assertEqual(pronounce_number(10000, ordinals=True),
                         "deset tisící")
        self.assertEqual(pronounce_number(18691, ordinals=True),
                         "osmnáct tisíc, šest sto a devadesát první")
        self.assertEqual(pronounce_number(1567, ordinals=True),
                         "jedna tisíc, pět sto a šedesát sedmý")
        self.assertEqual(pronounce_number(1.672e-27, places=3,
                                          scientific=True, ordinals=True),
                         "jedna tečka šest sedm dva krát deset k záporné "
                         "dvacet sedmý mocnině")
        self.assertEqual(pronounce_number(18e6, ordinals=True),
                         "osmnáct milliontý")
        self.assertEqual(pronounce_number(18e12, ordinals=True,
                                          short_scale=False),
                         "osmnáct biliontý")
        self.assertEqual(pronounce_number(18e12, ordinals=True),
                         "osmnáct trilliontý")
        self.assertEqual(pronounce_number(18e18, ordinals=True,
                                          short_scale=False), "osmnáct "
                                                              "triliontý")


class TestNiceDateFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read date_time_test.json files for test data
        cls.test_config = {}
        p = Path(date_time_format.config_path)
        for sub_dir in [x for x in p.iterdir() if x.is_dir()]:
            if (sub_dir / 'date_time_test.json').exists():
                print("Načítám test pro " +
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
                         "jedna dvacet dva")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "jedna dvacet dva p.m.")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "1:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:22 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:22")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:22")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "třináct dvacet dva")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "třináct dvacet dva")

        dt = datetime.datetime(2017, 1, 31,
                               13, 0, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "jedna hodin")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "jedna p.m.")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False),
                         "1:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:00 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:00")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:00")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "třináct sto")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "třináct sto")

        dt = datetime.datetime(2017, 1, 31,
                               13, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "jedna oh dva")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "jedna oh dva p.m.")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False),
                         "1:02")
        self.assertEqual(nice_time(dt, use_24hour=False, speech=False, use_ampm=True),
                         "1:02 PM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "13:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "13:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "třináct nula dva")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "třináct nula dva")

        dt = datetime.datetime(2017, 1, 31,
                               0, 2, 3, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "dvanáct oh dva")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "dvanáct oh dva a.m.")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "12:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "12:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "00:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "00:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "nula nula nula dva")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "nula nula nula dva")

        dt = datetime.datetime(2018, 2, 8,
                               1, 2, 33, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "jedna oh dva")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "jedna oh dva a.m.")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False),
                         "1:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=False, use_ampm=True),
                         "1:02 AM")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True),
                         "01:02")
        self.assertEqual(nice_time(dt, speech=False, use_24hour=True,
                                   use_ampm=True),
                         "01:02")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=True),
                         "nula jedna nula dva")
        self.assertEqual(nice_time(dt, use_24hour=True, use_ampm=False),
                         "nula jedna nula dva")

        dt = datetime.datetime(2017, 1, 31,
                               12, 15, 9, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "čtvrt po dvanáct")
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "čtvrt po dvanáct p.m.")

        dt = datetime.datetime(2017, 1, 31,
                               5, 30, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False, use_ampm=True),
                         "půl po pět a.m.")

        dt = datetime.datetime(2017, 1, 31,
                               1, 45, 00, tzinfo=default_timezone())
        self.assertEqual(nice_time(dt, use_24hour=False),
                         "třičtvrtě na dva")

    def test_nice_date(self):
        lang = "cs-cz"
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

        # test fall back to english !!!Skiped
        #dt = datetime.datetime(2018, 2, 4, 0, 2, 3, tzinfo=default_timezone())
        # self.assertEqual(nice_date(
        #    dt, lang='invalid', now=datetime.datetime(2018, 2, 4, 0, 2, 3)),
        #    'today')

        # test all days in a year for all languages,
        # that some output is produced
        # for lang in self.test_config:
        for dt in (datetime.datetime(2017, 12, 30, 0, 2, 3,
                   tzinfo=default_timezone()) +
                   datetime.timedelta(n) for n in range(368)):
            self.assertTrue(len(nice_date(dt, lang=lang)) > 0)

    def test_nice_date_time(self):
        lang = "cs-cz"
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
        lang = "cs-cz"
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

#                print(nice_year(dt, lang=lang))
    def test_nice_duration(self):

        self.assertEqual(nice_duration(1), "jedna sekunda")
        self.assertEqual(nice_duration(3), "tři sekundy")
        self.assertEqual(nice_duration(1, speech=False), "0:01")
        self.assertEqual(nice_duration(61), "jedna minuta jedna sekunda")
        self.assertEqual(nice_duration(61, speech=False), "1:01")
        self.assertEqual(nice_duration(5000),
                         "jedna hodina dvacet tři minuty dvacet sekundy")
        self.assertEqual(nice_duration(5000, speech=False), "1:23:20")
        self.assertEqual(nice_duration(50000),
                         "třináct hodiny padesát tři minuty dvacet sekundy")
        self.assertEqual(nice_duration(50000, speech=False), "13:53:20")
        self.assertEqual(nice_duration(500000,),
                         "pět dní  osmnáct hodiny padesát tři minuty dvacet sekundy")  # nopep8
        self.assertEqual(nice_duration(500000, speech=False), "5d 18:53:20")
        self.assertEqual(nice_duration(datetime.timedelta(seconds=500000),
                                       speech=False),
                         "5d 18:53:20")

    def test_join(self):
        self.assertEqual(join_list(None, "a"), "")
        self.assertEqual(join_list([], "a"), "")

        self.assertEqual(join_list(["a"], "a"), "a")
        self.assertEqual(join_list(["a", "b"], "a"), "a a b")
        self.assertEqual(join_list(["a", "b"], "nebo"), "a nebo b")

        self.assertEqual(join_list(["a", "b", "c"], "a"), "a, b a c")
        self.assertEqual(join_list(["a", "b", "c"], "nebo"), "a, b nebo c")
        self.assertEqual(
            join_list(["a", "b", "c"], "nebo", ";"), "a; b nebo c")
        self.assertEqual(
            join_list(["a", "b", "c", "d"], "nebo"), "a, b, c nebo d")

        self.assertEqual(join_list([1, "b", 3, "d"], "nebo"), "1, b, 3 nebo d")


if __name__ == "__main__":
    unittest.main()
