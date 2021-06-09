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
from datetime import datetime, timedelta

from lingua_franca import get_default_lang, set_default_lang, \
    load_language, unload_language
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import get_gender
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.time import default_timezone


def setUpModule():
    load_language("cs-cz")
    set_default_lang("cs")


def tearDownModule():
    unload_language("cs")


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("ty a já", "ty a já") >= 1.0)
        self.assertTrue(fuzzy_match("ty a já", "ty") < 0.5)
        self.assertTrue(fuzzy_match("Ty", "ty") >= 0.5)
        self.assertTrue(fuzzy_match("ty a já", "ty") ==
                        fuzzy_match("ty", "ty a já"))
        self.assertTrue(fuzzy_match("ty a já", "on nebo oni") < 0.23)

    def test_match_one(self):
        # test list of choices
        choices = ['frank', 'kate', 'harry', 'henry']
        self.assertEqual(match_one('frank', choices)[0], 'frank')
        self.assertEqual(match_one('fran', choices)[0], 'frank')
        self.assertEqual(match_one('enry', choices)[0], 'henry')
        self.assertEqual(match_one('katt', choices)[0], 'kate')
        # test dictionary of choices
        choices = {'frank': 1, 'kate': 2, 'harry': 3, 'henry': 4}
        self.assertEqual(match_one('frank', choices)[0], 1)
        self.assertEqual(match_one('enry', choices)[0], 4)


class TestNormalize(unittest.TestCase):

    def test_extract_number(self):
        self.assertEqual(extract_number("tohle je první test",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("tohle je 2 test"), 2)
        self.assertEqual(extract_number("tohle je druhý test",
                                        ordinals=True), 2)
        #self.assertEqual(extract_number("tohle je třetí test"), 1.0 / 3.0)
        self.assertEqual(extract_number("tohle je třetí test",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("ten čtvrtý", ordinals=True), 4.0)
        self.assertEqual(extract_number(
            "ten třicátý šestý", ordinals=True), 36.0)
        self.assertEqual(extract_number("tohle je test číslo 4"), 4)
        self.assertEqual(extract_number("jedna třetina šálku"), 1.0 / 3.0)
        self.assertEqual(extract_number("tři šálky"), 3)
        self.assertEqual(extract_number("1/3 šálku"), 1.0 / 3.0)
        self.assertEqual(extract_number("čtvrtina šálku"), 0.25)
        self.assertEqual(extract_number("1/4 cup"), 0.25)
        self.assertEqual(extract_number("jedna čtvrtina šálku"), 0.25)
        self.assertEqual(extract_number("2/3 šálků"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 šálků"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 a 3/4 šálků"), 1.75)
        self.assertEqual(extract_number("1 šálek a půl"), 1.5)
        self.assertEqual(extract_number("jeden šálek a polovina"), 1.5)
        self.assertEqual(extract_number("jedna a půl šálků"), 1.5)
        self.assertEqual(extract_number("jedna a jedna polovina šálků"), 1.5)
        self.assertEqual(extract_number("tři čtvrtina šálků"), 3.0 / 4.0)
        self.assertEqual(extract_number("tři čtvrtiny šálků"), 3.0 / 4.0)
        self.assertEqual(extract_number("dvacet dva"), 22)
        self.assertEqual(extract_number(
            "Dvacet dva s velkým písmenam na začátku"), 22)
        self.assertEqual(extract_number(
            "dvacet Dva s dva krát velkým písmem"), 22)
        self.assertEqual(extract_number(
            "dvacet Dva s různou velikostí písmen"), 22)
        self.assertEqual(extract_number("Dvacet dva a Tři Pětiny"), 22.6)
        self.assertEqual(extract_number("dvě sto"), 200)
        self.assertEqual(extract_number("devět tisíc"), 9000)
        self.assertEqual(extract_number("šest sto šedesát šest"), 666)
        self.assertEqual(extract_number("dva million"), 2000000)
        self.assertEqual(extract_number("dva million pět sto tisíc "
                                        "tun žhavého kovu"), 2500000)
        self.assertEqual(extract_number("šest trillion"), 6000000000000.0)
        self.assertEqual(extract_number("šest trilion", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("jedna tečka pět"), 1.5)
        self.assertEqual(extract_number("tři tečka čtrnáct"), 3.14)
        self.assertEqual(extract_number("nula tečka dva"), 0.2)
        self.assertEqual(extract_number("billion roků "),
                         1000000000.0)
        self.assertEqual(extract_number("bilion roků",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("jedno sto tisíc"), 100000)
        self.assertEqual(extract_number("mínus 2"), -2)
        self.assertEqual(extract_number("záporné sedmdesát"), -70)
        self.assertEqual(extract_number("tisíc million"), 1000000000)
        self.assertEqual(extract_number("miliarda", short_scale=False),
                         1000000000)
        self.assertEqual(extract_number("šestina třetina"),
                         1 / 6 / 3)
        self.assertEqual(extract_number("šestina třetí", ordinals=True),
                         3)
        self.assertEqual(extract_number("třicet sekund"), 30)
        self.assertEqual(extract_number("třicátý druhý", ordinals=True), 32)
        self.assertEqual(extract_number("tohle je billiontý test",
                                        ordinals=True), 1e09)
        print("tohle udělat později")
        #self.assertEqual(extract_number("tohle je billiontý test"), 1e-9)

        self.assertEqual(extract_number("tohle je biliontý test",
                                        ordinals=True,
                                        short_scale=False), 1e12)
        print("tohle udělat později")
        # self.assertEqual(extract_number("tohle je biliontý test",
        # short_scale=False), 1e-12)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("dvacet tisíc"), 20000)
        self.assertEqual(extract_number("padesát million"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("dvacet billion tři sto million \
                                        devět sto padesát tisíc šest sto \
                                        sedmdesát pět tečka osm"),
                         20300950675.8)
        self.assertEqual(extract_number("devět sto devadesát devět million devět \
                                        sto devadesát devět tisíc devět \
                                        sto devadesát devět tečka devět"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("osm sto trillion dva sto \
                                        padesát sedm"), 800000000000257.0)

        # TODO handle this case
        # self.assertEqual(
        #    extract_number("6 dot six six six"),
        #    6.666)
        self.assertTrue(extract_number("Tenisový hráč je rychlý") is False)
        self.assertTrue(extract_number("křehký") is False)

        self.assertTrue(extract_number("křehká nula") is not False)
        self.assertEqual(extract_number("křehká nula"), 0)

        #self.assertTrue(extract_number("grobo 0") is not False)
        #self.assertEqual(extract_number("grobo 0"), 0)

        self.assertEqual(extract_number("dvojice piv"), 2)
        self.assertEqual(extract_number("dvojice sto piv"), 200)
        self.assertEqual(extract_number("dvojice tisíc piv"), 2000)

        self.assertEqual(extract_number(
            "tohle je 7 test", ordinals=True), 7)
        self.assertEqual(extract_number(
            "tohle je 7 test", ordinals=False), 7)
        self.assertTrue(extract_number("tohle je n. test") is False)
        self.assertEqual(extract_number("tohle je 1. test"), 1)
        self.assertEqual(extract_number("tohle je 2. test"), 2)
        self.assertEqual(extract_number("tohle je 3. test"), 3)
        self.assertEqual(extract_number("tohle je 31. test"), 31)
        self.assertEqual(extract_number("tohle je 32. test"), 32)
        self.assertEqual(extract_number("tohle je 33. test"), 33)
        self.assertEqual(extract_number("tohle je 34. test"), 34)
        self.assertEqual(extract_number("celkem 100%"), 100)

    def test_extract_duration_cs(self):
        self.assertEqual(extract_duration("10 sekund"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minut"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 hodiny"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 dny"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 týdnů"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("sedm hodin"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 sekund"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("osm a polovina dne třicet"
                                          " devět sekund"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("Nastav časovač na 30 minut"),
                         (timedelta(minutes=30), "nastav časovač na"))
        self.assertEqual(extract_duration("Čtyři a půl minuty do"
                                          " západu"),
                         (timedelta(minutes=4.5), "do západu"))
        self.assertEqual(extract_duration("devatenáct minut po hodině"),
                         (timedelta(minutes=19), "po hodině"))
        self.assertEqual(extract_duration("vzbuď mě za tři týdny, čtyři"
                                          " sto devadesát sedm dní, a"
                                          " tři sto 91.6 sekund"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "vzbuď mě za , , a"))
        self.assertEqual(extract_duration("film je jedna hodina, padesát sedm"
                                          " a půl minuty dlouhý"),
                         (timedelta(hours=1, minutes=57.5),
                             "film je ,  dlouhý"))
        self.assertEqual(extract_duration("10-sekund"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minut"),
                         (timedelta(minutes=5), ""))

    def test_extractdatetime_cs(self):
        def extractWithFormat(text):
            # Tue June 27, 2017 @ 1:04pm
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("nyní je čas",
                    "2017-06-27 13:04:00", "je čas")
        testExtract("za sekundu",
                    "2017-06-27 13:04:01", "")
        testExtract("za minutu",
                    "2017-06-27 13:05:00", "")
        # testExtract("ve dvou minutách",
        #            "2017-06-27 13:06:00", "")
        # testExtract("in a couple of minutes",
        #            "2017-06-27 13:06:00", "")
        # testExtract("ve dvou hodinách",
        #            "2017-06-27 15:04:00", "")
        # testExtract("in a couple of hours",
        #            "2017-06-27 15:04:00", "")
        # testExtract("v dvoje týden",
        #            "2017-07-11 00:00:00", "")
        # testExtract("in a couple of weeks",
        #            "2017-07-11 00:00:00", "")
        # testExtract("v dvoje měsíc",
        #            "2017-08-27 00:00:00", "")
        # testExtract("v dvoje rok",
        #            "2019-06-27 00:00:00", "")
        # testExtract("in a couple of months",
        #            "2017-08-27 00:00:00", "")
        # testExtract("in a couple of years",
        #            "2019-06-27 00:00:00", "")
        testExtract("v desetiletí",
                    "2027-06-27 00:00:00", "")
        # testExtract("in a couple of decades",
        #            "2037-06-27 00:00:00", "")
        testExtract("další desetiletí",
                    "2027-06-27 00:00:00", "")
        testExtract("v století",
                    "2117-06-27 00:00:00", "")
        testExtract("v tisíciletí",
                    "3017-06-27 00:00:00", "")
        testExtract("v dvoje desetiletí",
                    "2037-06-27 00:00:00", "")
        testExtract("v 5 desetiletí",
                    "2067-06-27 00:00:00", "")
        testExtract("v dvoje století",
                    "2217-06-27 00:00:00", "")
        # testExtract("in a couple of centuries",
        #            "2217-06-27 00:00:00", "")
        testExtract("v 2 století",
                    "2217-06-27 00:00:00", "")
        testExtract("v dvoje tisíciletí",
                    "4017-06-27 00:00:00", "")
        # testExtract("in a couple of millenniums",
        #            "4017-06-27 00:00:00", "")
        testExtract("v hodina",
                    "2017-06-27 14:04:00", "")
        testExtract("chci to během hodiny",
                    "2017-06-27 14:04:00", "chci to")
        testExtract("za 1 sekundu",
                    "2017-06-27 13:04:01", "")
        testExtract("za 2 sekundy",
                    "2017-06-27 13:04:02", "")
        testExtract("Nastav časovač na 1 minutu",
                    "2017-06-27 13:05:00", "nastav časovač")
        testExtract("Nastav časovač na půl hodina",
                    "2017-06-27 13:34:00", "nastav časovač")
        testExtract("Nastav časovač na 5 den od dnes",
                    "2017-07-02 00:00:00", "nastav časovač")
        testExtract("den po zítřku",
                    "2017-06-29 00:00:00", "")
        testExtract("Jaké je počasí den po zítřku?",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("Připomeň mi v 10:45 pm",
                    "2017-06-27 22:45:00", "připomeň mi")
        testExtract("jaké je počasí v pátek ráno",
                    "2017-06-30 08:00:00", "jaké je počasí")
        testExtract("jaké je zítřejší počasí",
                    "2017-06-28 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí toto odpoledne",
                    "2017-06-27 15:00:00", "jaké je počasí")
        testExtract("jaké je počasí tento večer",
                    "2017-06-27 19:00:00", "jaké je počasí")
        testExtract("jaké bylo počasí toto ráno",
                    "2017-06-27 08:00:00", "jaké bylo počasí")
        testExtract("připomeň mi abych zavolal mámě v 8 týden a 2 dny",
                    "2017-08-24 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v srpen 3",
                    "2017-08-03 00:00:00", "připomeň mi abych zavolal mámě")  # přidat i třetího slovně
        testExtract("připomeň mi zítra abych zavolal mámě v 7am",
                    "2017-06-28 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi zítra abych zavolal mámě v 10pm",
                    "2017-06-28 22:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7am",
                    "2017-06-28 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v hodina",
                    "2017-06-27 14:04:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 1730",
                    "2017-06-27 17:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 0630",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 06 30 hodina",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 06 30",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 06 30 hodina",
                    "2017-06-28 06:30:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7 hodin",
                    "2017-06-27 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě večer v 7 hodin",
                    "2017-06-27 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě  v 7 hodin večer",
                    "2017-06-27 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7 hodin ráno",
                    "2017-06-28 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v Čtvrtek večer v 7 hodin",
                    "2017-06-29 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v Čtvrtek ráno v 7 hodin",
                    "2017-06-29 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7 hodin Čtvrtek ráno",
                    "2017-06-29 07:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 7:00 Čtvrtek ráno",
                    "2017-06-29 07:00:00", "připomeň mi abych zavolal mámě")
        # TODO: This test is imperfect due to "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("připomeň mi abych zavolal mámě v 7:00 Čtvrtek večer",
                    "2017-06-29 19:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 Středa večer",
                    "2017-06-28 20:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 Středa v večer",
                    "2017-06-28 20:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě Středa večer v 8",
                    "2017-06-28 20:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za dvě hodiny",
                    "2017-06-27 15:04:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za 2 hodiny",
                    "2017-06-27 15:04:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za 15 minut",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za patnáct minut",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za půl hodina",
                    "2017-06-27 13:34:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za půl hodina",
                    "2017-06-27 13:34:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za čtvrt hodina",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě za čtvrt hodina",
                    "2017-06-27 13:19:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am 2 den po této sobota",
                    "2017-07-03 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("Přehraj Rick Astley hudbu 2 dny od Pátek",
                    "2017-07-02 00:00:00", "přehraj rick astley hudbu")
        testExtract("Začni invazi v 3:45 pm v Čtvrtek",
                    "2017-06-29 15:45:00", "začni invazi")
        testExtract("V Pondělí, objednej koláč z pekárny",
                    "2017-07-03 00:00:00", "objednej koláč z pekárny")
        testExtract("Přehraj Happy Birthday hudbu 5 roků od dnes",
                    "2022-06-27 00:00:00", "přehraj happy birthday hudbu")
        testExtract("Skype Mámě v 12:45 pm další Čtvrtek",
                    "2017-07-06 12:45:00", "skype mámě")
        testExtract("Jaké je počasí příští Pátek?",
                    "2017-06-30 00:00:00", "jaké je počasí")
        testExtract("Jaké je počasí příští Středa?",
                    "2017-07-05 00:00:00", "jaké je počasí")
        testExtract("Jaké je počasí příští Čtvrtek?",
                    "2017-07-06 00:00:00", "jaké je počasí")
        testExtract("Jaké je počasí příští pátek ráno",
                    "2017-06-30 08:00:00", "jaké je počasí")
        testExtract("jaké je počasí příští pátek večer",
                    "2017-06-30 19:00:00", "jaké je počasí")
        testExtract("jaké je počasí příští pátek odpoledne",
                    "2017-06-30 15:00:00", "jaké je počasí")
        testExtract("připomeň mi abych zavolal mámě v srpen třetího",
                    "2017-08-03 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("Kup ohňostroj v 4 Červenec",
                    "2017-07-04 00:00:00", "kup ohňostroj")
        testExtract("jaké je počasí 2 týdny od další pátek",
                    "2017-07-14 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí Středa v 0700 hodina",
                    "2017-06-28 07:00:00", "jaké je počasí")
        testExtract("Nastav budík Středa v 7 hodin",
                    "2017-06-28 07:00:00", "nastav budík")
        testExtract("Nastav schůzku v 12:45 pm další Čtvrtek",
                    "2017-07-06 12:45:00", "nastav schůzku")
        testExtract("Jaké je počasí tento Čtvrtek?",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("nastav návštěvu na 2 týdny a 6 dní od Sobota",
                    "2017-07-21 00:00:00", "nastav návštěvu")
        testExtract("Zahaj invazi v 03 45 v Čtvrtek",
                    "2017-06-29 03:45:00", "zahaj invazi")
        testExtract("Zahaj invazi v 800 hodin v Čtvrtek",
                    "2017-06-29 08:00:00", "zahaj invazi")
        testExtract("Zahaj párty v 8 hodin v večer v Čtvrtek",
                    "2017-06-29 20:00:00", "zahaj párty")
        testExtract("Zahaj invazi v 8 v večer v Čtvrtek",
                    "2017-06-29 20:00:00", "zahaj invazi")
        testExtract("Zahaj invazi v Čtvrtek v poledne",
                    "2017-06-29 12:00:00", "zahaj invazi")
        testExtract("Zahaj invazi v Čtvrtek v půlnoc",
                    "2017-06-29 00:00:00", "zahaj invazi")
        testExtract("Zahaj invazi v Čtvrtek v 0500",
                    "2017-06-29 05:00:00", "zahaj invazi")
        testExtract("připomeň mi abych vstal v 4 roky",
                    "2021-06-27 00:00:00", "připomeň mi abych vstal")
        testExtract("připomeň mi abych vstal v 4 roky a 4 dny",
                    "2021-07-01 00:00:00", "připomeň mi abych vstal")
        testExtract("jaké je počasí 3 dny po zítra?",
                    "2017-07-01 00:00:00", "jaké je počasí")
        testExtract("prosinec 3",
                    "2017-12-03 00:00:00", "")
        testExtract("sejdeme se v 8:00 dnes večer",
                    "2017-06-27 20:00:00", "sejdeme se")
        testExtract("sejdeme se v 5pm",
                    "2017-06-27 17:00:00", "sejdeme se")
        testExtract("sejdeme se v 8 am",
                    "2017-06-28 08:00:00", "sejdeme se")
        testExtract("připomeň mi abych vstal v 8 am",
                    "2017-06-28 08:00:00", "připomeň mi abych vstal")
        testExtract("jaké je počasí v úterý",
                    "2017-06-27 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí v pondělí",
                    "2017-07-03 00:00:00", "jaké je počasí")
        testExtract("jaké je počasí toto Středa",
                    "2017-06-28 00:00:00", "jaké je počasí")
        testExtract("v Čtvrtek jaké je počasí",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("tento Čtvrtek jaké je počasí",
                    "2017-06-29 00:00:00", "jaké je počasí")
        testExtract("poslední pondělí jaké bylo počasí",
                    "2017-06-26 00:00:00", "jaké bylo počasí")
        testExtract("nastav budík na Středa večer v 8",
                    "2017-06-28 20:00:00", "nastav budík")
        testExtract("nastav budík na Středa v 3 hodiny v odpoledne",
                    "2017-06-28 15:00:00", "nastav budík")
        testExtract("nastav budík na Středa v 3 hodiny v ráno",
                    "2017-06-28 03:00:00", "nastav budík")
        testExtract("nastav budík na Středa ráno v 7 hodin",
                    "2017-06-28 07:00:00", "nastav budík")
        testExtract("nastav budík na dnes v 7 hodin",
                    "2017-06-27 19:00:00", "nastav budík")
        testExtract("nastav budík na tento večer v 7 hodin",
                    "2017-06-27 19:00:00", "nastav budík")
        # TODO: This test is imperfect due to the "at 7:00" still in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("nastav budík na tento večer v 7:00",
                    "2017-06-27 19:00:00", "nastav budík v 7:00")
        testExtract("večer v červen 5 2017 připomeň mi" +
                    " abych zavolal mámě",
                    "2017-06-05 19:00:00", "připomeň mi abych zavolal mámě")
        # TODO: This test is imperfect due to the missing "for" in the
        #       remainder.  But let it pass for now since time is correct
        testExtract("aktualizuj můj kalendář na ranní schůzku s julius" +
                    " v březnu 4",
                    "2018-03-04 08:00:00",
                    "aktualizuj můj kalendář schůzku s julius")
        testExtract("připomeň mi abych zavolal mámě další úterý",
                    "2017-07-04 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě  3 týdny",
                    "2017-07-18 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 týdny",
                    "2017-08-22 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 8 týdny a 2 dny",
                    "2017-08-24 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 4 dny",
                    "2017-07-01 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 3 měsíce",
                    "2017-09-27 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 2 roky a 2 dny",
                    "2019-06-29 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě další týden",
                    "2017-07-04 00:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am v Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am tato Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10 další Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("připomeň mi abych zavolal mámě v 10am další Sobota",
                    "2017-07-01 10:00:00", "připomeň mi abych zavolal mámě")
        # test yesterday
        testExtract("jaký den byl včera",
                    "2017-06-26 00:00:00", "jaký den byl")
        testExtract("jaký den byl den před včera",
                    "2017-06-25 00:00:00", "jaký den byl")
        testExtract("měl jsem večeři včera v 6",
                    "2017-06-26 06:00:00", "měl jsem večeři")
        testExtract("měl jsem večeři včera v 6 am",
                    "2017-06-26 06:00:00", "měl jsem večeři")
        testExtract("měl jsem večeři včera v 6 pm",
                    "2017-06-26 18:00:00", "měl jsem večeři")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight

        testExtract("nastav budík na 9 o víkendech",
                    "2017-06-27 21:00:00", "nastav budík víkendech")
        testExtract("na 8 dnes večer",
                    "2017-06-27 20:00:00", "")
        testExtract("na 8:30pm dnes večer",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("nastav budík na dnes večer 9:30",
                    "2017-06-27 21:30:00", "nastav budík")
        testExtract("nastav budík na 9:00 na dnes večer",
                    "2017-06-27 21:00:00", "nastav budík")
        # Check if it picks intent irrespective of correctness
        testExtract("nastav budík na 9 hodin dnes večer",
                    "2017-06-27 21:00:00", "nastav budík")
        testExtract("připomeň mi hru dnes v noci v 11:30",
                    "2017-06-27 23:30:00", "připomeň mi hru")
        testExtract("nastav budík v 7:30 o výkendech",
                    "2017-06-27 19:30:00", "nastav budík o výkendech")

        #  "# days <from X/after X>"
        testExtract("mé narozeniny jsou 2 dny od dnes",
                    "2017-06-29 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny po dnes",
                    "2017-06-29 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny od zítra",
                    "2017-06-30 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny od zítra",
                    "2017-06-30 00:00:00", "mé narozeniny jsou")
        testExtract("připomeň mi abych zavolal mámě v 10am 2 dny po další Sobota",
                    "2017-07-10 10:00:00", "připomeň mi abych zavolal mámě")
        testExtract("mé narozeniny jsou 2 dny od včera",
                    "2017-06-28 00:00:00", "mé narozeniny jsou")
        testExtract("mé narozeniny jsou 2 dny po včera",
                    "2017-06-28 00:00:00", "mé narozeniny jsou")

        #  "# days ago>"
        testExtract("mé narozeniny byly před 1 den",
                    "2017-06-26 00:00:00", "mé narozeniny byly")
        testExtract("mé narozeniny byly před 2 dny",
                    "2017-06-25 00:00:00", "mé narozeniny byly")
        testExtract("mé narozeniny byly před 3 dny",
                    "2017-06-24 00:00:00", "mé narozeniny byly")
        testExtract("mé narozeniny byly před 4 dny",
                    "2017-06-23 00:00:00", "mé narozeniny byly")
        # TODO this test is imperfect due to "tonight" in the reminder, but let is pass since the date is correct
        testExtract("sejdeme se dnes v noci",
                    "2017-06-27 22:00:00", "sejdeme se noci")
        # TODO this test is imperfect due to "at night" in the reminder, but let is pass since the date is correct
        testExtract("sejdeme se později v noci",
                    "2017-06-27 22:00:00", "sejdeme se později v noci")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("Jaké bude počasí zítra v noci",
                    "2017-06-28 22:00:00", "jaké bude počasí v noci")
        # TODO this test is imperfect due to "night" in the reminder, but let is pass since the date is correct
        testExtract("jaké bude počasí příští úterý v noci",
                    "2017-07-04 22:00:00", "jaké bude počasí v noci")

    def test_extract_ambiguous_time_cs(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        večer = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('krmení ryb'), None)
        self.assertEqual(
            extract_datetime('den'), None)
        self.assertEqual(
            extract_datetime('týden'), None)
        self.assertEqual(
            extract_datetime('měsíc'), None)
        self.assertEqual(
            extract_datetime('rok'), None)
        self.assertEqual(
            extract_datetime(' '), None)
        self.assertEqual(
            extract_datetime('nakrmit ryby v 10 hodin', morning)[0],
            datetime(2017, 6, 27, 10, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('nakrmit ryby v 10 hodin', noonish)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('nakrmit ryby v 10 hodin', večer)[0],
            datetime(2017, 6, 27, 22, 0, 0, tzinfo=default_timezone()))

    """
    In Czech is May and may have different format
    def test_extract_date_with_may_I_cs(self):
        now = datetime(2019, 7, 4, 8, 1, 2)
        may_date = datetime(2019, 5, 2, 10, 11, 20)
        self.assertEqual(
            extract_datetime('Můžu vědět jaký je to čas zítra', now)[0],
            datetime(2019, 7, 5, 0, 0, 0))
        self.assertEqual(
            extract_datetime('Můžu vědět kdy je 10 hodin', now)[0],
            datetime(2019, 7, 4, 10, 0, 0))
        self.assertEqual(
            extract_datetime('24. můžu chtít připomenutí', may_date)[0],
            datetime(2019, 5, 24, 0, 0, 0))
    """

    def test_extract_relativedatetime_cs(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("sejdeme se za 5 minut",
                    "2017-06-27 10:06:02", "sejdeme se")
        testExtract("sejdeme se za 5minut",
                    "2017-06-27 10:06:02", "sejdeme se")
        testExtract("sejdeme se za 5 sekund",
                    "2017-06-27 10:01:07", "sejdeme se")
        testExtract("sejdeme se za 1 hodinu",
                    "2017-06-27 11:01:02", "sejdeme se")
        testExtract("sejdeme se za 2 hodiny",
                    "2017-06-27 12:01:02", "sejdeme se")
        print("TODO")  # Need better normaliting procedure for czech inflexion
        # testExtract("sejdeme se za 2hodiny",
        #            "2017-06-27 12:01:02", "sejdeme se")
        testExtract("sejdeme se za 1 minutu",
                    "2017-06-27 10:02:02", "sejdeme se")
        testExtract("sejdeme se za 1 sekundu",
                    "2017-06-27 10:01:03", "sejdeme se")
        testExtract("sejdeme se za 5sekund",
                    "2017-06-27 10:01:07", "sejdeme se")

    def test_spaces(self):
        self.assertEqual(normalize("  tohle   je   test"),
                         "tohle je test")
        self.assertEqual(normalize("  tohle   je     test  "),
                         "tohle je test")
        self.assertEqual(normalize("  tohle   je  jedna    test"),
                         "tohle je 1 test")

    def test_numbers(self):
        self.assertEqual(normalize("tohle je jedna dva tři  test"),
                         "tohle je 1 2 3 test")
        self.assertEqual(normalize("  to je čtyři pět šest  test"),
                         "to je 4 5 6 test")
        self.assertEqual(normalize("to je sedum osum devět test"),
                         "to je 7 8 9 test")
        self.assertEqual(normalize("to je sedm osm devět  test"),
                         "to je 7 8 9 test")
        self.assertEqual(normalize("tohle je deset jedenáct dvanáct test"),
                         "tohle je 10 11 12 test")
        self.assertEqual(normalize("tohle je třináct čtrnáct test"),
                         "tohle je 13 14 test")
        self.assertEqual(normalize("tohle je patnáct šestnáct sedmnáct"),
                         "tohle je 15 16 17")
        self.assertEqual(normalize("tohle je osmnáct devatenáct dvacet"),
                         "tohle je 18 19 20")
        self.assertEqual(normalize("tohle je jedna devatenáct dvacet dva"),
                         "tohle je 1 19 20 2")
        self.assertEqual(normalize("tohle je jedna sto"),
                         "tohle je 1 sto")
        self.assertEqual(normalize("tohle je jedna dva dvacet dva"),
                         "tohle je 1 2 20 2")
        self.assertEqual(normalize("tohle je jedna a půl"),
                         "tohle je 1 a půl")
        self.assertEqual(normalize("tohle je jedna a půl a pět šest"),
                         "tohle je 1 a půl a 5 6")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("tohle je jedna dva tři test"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("to je čtyři pět šest test"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("tohle je deset jedenáct dvanáct test"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("tohle je jedna dvacet jedna test"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 pes, sedm prasat, macdonald měl "
                                         "farmu, 3 krát 5 makaréna"),
                         [1, 7, 3, 5])
        self.assertEqual(extract_numbers("dva piva pro dva medvědy"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("dvacet 20 dvacet"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("dvacet 20 22"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("dvacet dvacet dva dvacet"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("dvacet 2"),
                         [22.0])
        self.assertEqual(extract_numbers("dvacet 20 dvacet 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("třetina jedna"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("třetí", ordinals=True), [3])
        self.assertEqual(extract_numbers("šest trillion", short_scale=True),
                         [6e12])
        self.assertEqual(extract_numbers("šest trilion", short_scale=False),
                         [6e18])
        self.assertEqual(extract_numbers("dvě prasátka a šest trillion bakterií",
                                         short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("dvě prasátka a šest trilion bakterií",
                                         short_scale=False), [2, 6e18])
        self.assertEqual(extract_numbers("třicátý druhý nebo první",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("tohle je sedm osm devět a"
                                         " půl test"),
                         [7.0, 8.0, 9.5])


if __name__ == "__main__":
    unittest.main()
