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
# See the License for the specific language governing permissions and
# limitations under the License.
#
import unittest
from datetime import datetime, timedelta
from dateutil import tz

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.internal import FunctionNotLocalizedError
from lingua_franca.time import default_timezone
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import get_gender
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize


def setUpModule():
    # TODO spin off English tests
    load_language('az')
    set_default_lang('az')


def tearDownModule():
    unload_language('az')


class TestFuzzyMatch(unittest.TestCase):
    def test_matches(self):
        self.assertTrue(fuzzy_match("sən və mən", "sən və mən") >= 1.0)
        self.assertTrue(fuzzy_match("sən və mən", "sən") < 0.5)
        self.assertTrue(fuzzy_match("sən", "sən") > 0.5)
        self.assertTrue(fuzzy_match("sən və mən", "sən") ==
                        fuzzy_match("sən", "sən və mən"))
        self.assertTrue(fuzzy_match("sən və mən", "he ya onlar") < 0.2)

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

        self.assertEqual(extract_number("bu 2 sınaqdır"), 2)
        self.assertEqual(extract_number("bu 4 nömrəli sınaqdır"), 4)
        self.assertEqual(extract_number("üç fıncan"), 3)
        self.assertEqual(extract_number("1/3 fıncan"), 1.0 / 3.0)
        self.assertEqual(extract_number("dörddəbir fıncan"), 0.25)
        self.assertEqual(extract_number("1/4 fıncan"), 0.25)
        self.assertEqual(extract_number("dörddə bir fincan"), 0.25)
        self.assertEqual(extract_number("2/3 fincan"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 fincan"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 və 3/4 fincan"), 1.75)
        self.assertEqual(extract_number("1 yarım fincan"), 1.5)
        self.assertEqual(extract_number("bir yarım fincan"), 1.5)
        self.assertEqual(extract_number("dörddə üç fincan"), 3.0 / 4.0)
        self.assertEqual(extract_number("iyirmi iki"), 22)

        # TODO 'İ'.lower() returns 2 chars, gets fixed in python3.10(unicode v14)
        # self.assertEqual(extract_number(
        #     "İyirmi iki böyük hərflə iyirmi"), 22)
        # self.assertEqual(extract_number(
        #     "iyirmi İki böyük hərflə iki"), 22)
        # self.assertEqual(extract_number(
        #     "İyirmi İki böyük hərflə ikisidə"), 22)

        self.assertEqual(extract_number("iki yüz"), 200)
        self.assertEqual(extract_number("doqquz min"), 9000)
        self.assertEqual(extract_number("altı yüz altmış altı"), 666)
        self.assertEqual(extract_number("iki milyon"), 2000000)
        self.assertEqual(extract_number("iki milyon beş yüz min "
                                        "tons dəmir"), 2500000)
        self.assertEqual(extract_number("altı trilyon"), 6000000000000)
        self.assertEqual(extract_number("altı trilyon", short_scale=False),
                         6e+18)
        self.assertEqual(extract_number("bir nöqtə beş"), 1.5)
        self.assertEqual(extract_number("üç nöqtə on dörd"), 3.14)
        self.assertEqual(extract_number("sıfır nöqtə iki"), 0.2)
        self.assertEqual(extract_number("bir milyard yaş daha böyükdür"),
                         1000000000.0)
        self.assertEqual(extract_number("bir milyard yaş daha böyükdür",
                                        short_scale=False),
                         1000000000000.0)
        self.assertEqual(extract_number("yüz min"), 100000)
        self.assertEqual(extract_number("minus 2"), -2)
        self.assertEqual(extract_number("mənfi yetmiş"), -70)
        self.assertEqual(extract_number("min milyon"), 1000000000)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("iyirmi min"), 20000)
        self.assertEqual(extract_number("əlli milyon"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("iyirmi milyard üç yüz milyon \
                                        doqquz yüz əlli min altı yüz \
                                        yetmiş beş nöqtə səkkiz"),
                         20300950675.8)
        self.assertEqual(extract_number("doqquz yüz doxsan doqquz milyon doqquz \
                                        yüz doxsan doqquz min doqquz \
                                        yüz doxsan doqquz nöqtə doqquz"),
                         999999999.9)

        # TODO why does "trilyon" result in xxxx.0?
        self.assertEqual(extract_number("səkkiz yüz trilyon iki yüz \
                                        əlli yeddi"), 800000000000257.0)

        # TODO handle this case
        # self.assertEqual(
        #    extract_number("altı altı altı"), 666)
        
        self.assertTrue(extract_number("Tennisçi sürətlidir") is False)
        self.assertTrue(extract_number("parçalamaq") is False)

        self.assertTrue(extract_number("parçalamaq sıfır") is not False)
        self.assertEqual(extract_number("parçalamaq sıfır"), 0)

        self.assertTrue(extract_number("grobo 0") is not False)
        self.assertEqual(extract_number("grobo 0"), 0)

        self.assertEqual(extract_number("tamamilə 100%"), 100)

    def test_extract_duration_az(self):
        self.assertEqual(extract_duration("10 saniyə"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 dəqiqə"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 saat"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 gün"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 həftə"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("yeddi saat"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 saniyə"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("səkkiz yarım gün otuz"
                                          " doqquz saniyə"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("üç həftə, dörd yüz doxsan yeddi gün, "
                                          "üç yüz 91.6 saniyə sonra məni oyandır"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "sonra məni oyandır"))
        self.assertEqual(extract_duration("10-saniyə"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-dəqiqə"),
                         (timedelta(minutes=5), ""))

    def test_extract_duration_case_az(self):
        self.assertEqual(extract_duration("taymeri 30 dəqiqəyə qur"),
                         (timedelta(minutes=30), "taymeri qur"))
        self.assertEqual(extract_duration("Film bir saat, əlli yeddi"
                                          " yarım dəqiqə davam edir"),
                         (timedelta(hours=1, minutes=57.5),
                             "Film davam edir"))
        self.assertEqual(extract_duration("Gün batana dörd dəqiqə yarım qaldı"),
                         (timedelta(minutes=4.5), "Gün batana  qaldı"))
        self.assertEqual(extract_duration("Saatı on doqquz dəqiqə keçir"),
                         (timedelta(minutes=19), "Saatı keçir"))

    def test_extractdatetime_fractions_az(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("yarım saat sonra pusu qur",
                    "2017-06-27 13:34:00", "pusu qur")
        testExtract("yarım saat sora anama zəng etməyi xatırlat",
                    "2017-06-27 13:34:00", "anama zəng etməyi xatırlat")

    def test_extractdatetime_az(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            print(res)
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("indi vaxtıdır",
                    "2017-06-27 13:04:00", "vaxtıdır")
        testExtract("bir saniyəyə",
                    "2017-06-27 13:04:01", "")
        testExtract("bir dəqiqəyə",
                    "2017-06-27 13:05:00", "")
        testExtract("gələn onillikə",
                    "2027-06-27 00:00:00", "")
        testExtract("gələn yüzillikə",
                    "2117-06-27 00:00:00", "")
        testExtract("gələn minillikə",
                    "3017-06-27 00:00:00", "")
        testExtract("5 onillikə",
                    "2067-06-27 00:00:00", "")
        testExtract("2 yüzillikə",
                    "2217-06-27 00:00:00", "")
        testExtract("bir saata",
                    "2017-06-27 14:04:00", "")
        testExtract("bir saat ərzində istəyirəm",
                    "2017-06-27 14:04:00", "istəyirəm")
        testExtract("1 saniyəyə",
                    "2017-06-27 13:04:01", "")
        testExtract("2 saniyəyə",
                    "2017-06-27 13:04:02", "")
        testExtract("Pusunu 1 dəqiqə sonraya qur",
                    "2017-06-27 13:05:00", "pusunu qur")
        testExtract("5 gün sonraya pusu qur",
                    "2017-07-02 00:00:00", "pusu qur")
        testExtract("birigün",
                    "2017-06-29 00:00:00", "")
        testExtract("birigün hava necə olacaq?",
                    "2017-06-29 00:00:00", "hava necə olacaq")
        testExtract("Axşam 10:45 də yadıma sal",
                    "2017-06-27 22:45:00", "yadıma sal")
        testExtract("cümə səhər hava necədir",
                    "2017-06-30 08:00:00", "hava necədir")
        testExtract("sabah hava necedir",
                    "2017-06-28 00:00:00", "hava necedir")
        testExtract("bu günortadan sonra hava necədir",
                    "2017-06-27 15:00:00", "hava necədir")
        testExtract("bu axşam hava necədir",
                    "2017-06-27 19:00:00", "hava necədir")
        testExtract("bu səhər hava neceydi",
                    "2017-06-27 08:00:00", "hava neceydi")
        testExtract("8 həftə 2 gün sonra anama zəng etməyi xatırlat",
                    "2017-08-24 00:00:00", "anama zəng etməyi xatırlat")
        testExtract("3 avqustda anama zəng etməyi xatırlat",
                    "2017-08-03 00:00:00", "anama zəng etməyi xatırlat")
        testExtract("sabah 7 də anama zəng etməyi xatırlat",
                    "2017-06-28 07:00:00", "anama zəng etməyi xatırlat")
        testExtract("sabah axşam saat 10 da anama zəng etməyi xatırlat",
                    "2017-06-28 22:00:00", "anama zəng etməyi xatırlat")
        testExtract("səhər 7 də anama zəng etməyi xatırlat ",
                    "2017-06-28 07:00:00", "anama zəng etməyi xatırlat")
        testExtract("bir saatdan sonra anama zəng etməyi xatırlat",
                    "2017-06-27 14:04:00", "anama zəng etməyi xatırlat")
        testExtract("anama 17 30 da zəng etməyi xatırlat",
                    "2017-06-27 17:30:00", "anama zəng etməyi xatırlat")
        testExtract("anama 06 30 da zəng etməyi xatırlat",
                    "2017-06-28 06:30:00", "anama zəng etməyi xatırlat")
        testExtract("06 30 da anama zəng etməyi xatırlat",
                    "2017-06-28 06:30:00", "anama zəng etməyi xatırlat")
        testExtract("Cümə axşamı səhər 7:00 də anama zəng etməyi xatırlat",
                    "2017-06-29 07:00:00", "anama zəng etməyi xatırlat")
        testExtract("çərşənbə axşam 8 də anama zəng etməyi xatırlat",
                    "2017-06-28 20:00:00", "anama zəng etməyi xatırlat")
        testExtract("iki saatdan sonra anama zəng etməyi xatırlat",
                    "2017-06-27 15:04:00", "anama zəng etməyi xatırlat")
        testExtract("2 saatdan sonra anama zəng etməyi xatırlat",
                    "2017-06-27 15:04:00", "anama zəng etməyi xatırlat")
        testExtract("15 dəqiqə sonra anama zəng etməyi xatırlat",
                    "2017-06-27 13:19:00", "anama zəng etməyi xatırlat")
        testExtract("on beş dəqiqədən sonra anama zəng etməyi xatırlat",
                    "2017-06-27 13:19:00", "anama zəng etməyi xatırlat")
        testExtract("bu şənbə günündən 2 gün sonra səhər 10 da anama zəng etməyi xatırlat",
                    "2017-07-03 10:00:00", "anama zəng etməyi xatırlat")
        testExtract("Cümə günündən 2 gün sonra Rick Astley musiqisini çal",
                    "2017-07-02 00:00:00", "rick astley musiqisini çal")
        testExtract("Cümə axşamı günü saat 15:45 də hücuma başlayın",
                    "2017-06-29 15:45:00", "hücuma başlayın")
        testExtract("Bazar ertəsi günü çörəkxanadan çörək sifariş vər",
                    "2017-07-03 00:00:00", "çörəkxanadan çörək sifariş vər")
        testExtract("Bu gündən 5 il sonra Happy Birthday musiqisini çal",
                    "2022-06-27 00:00:00", "happy birthday musiqisini çal")
        testExtract("gələn cümə səhər hava necədir",
                    "2017-06-30 08:00:00", "hava necədir")
        testExtract("gələn cümə axşam hava necədir",
                    "2017-06-30 19:00:00", "hava necədir")
        testExtract("gələn cümə günortadan sonra hava necədir ",
                    "2017-06-30 15:00:00", "hava necədir")
        testExtract("iyulun 4 də atəşfəşanlıq al",
                    "2017-07-04 00:00:00", "atəşfəşanlıq al")
        testExtract("gələn cümə günündən 2 həftə sonra hava necədir",
                    "2017-07-14 00:00:00", "hava necədir")
        testExtract("çərşənbə günü saat 07 00 də hava necədir",
                    "2017-06-28 07:00:00", "hava necədir")
        testExtract("Gələn cümə axşamı saat 12:45 də görüş təyin ed",
                    "2017-07-06 12:45:00", "görüş təyin ed")
        testExtract("Bu cümə axşamı hava necədir?",
                    "2017-06-29 00:00:00", "hava necədir")
        testExtract("Cümə axşamı 03 45 də hücuma başlayın",
                    "2017-06-29 03:45:00", "hücuma başlayın")
        testExtract("Cümə axşamı axşam 8 də hücuma başlayın",
                    "2017-06-29 20:00:00", "hücuma başlayın")
        testExtract("Cümə axşamı günortada hücuma başlayın",
                    "2017-06-29 12:00:00", "hücuma başlayın")
        testExtract("Cümə axşamı gecə yarısında hücuma başlayın",
                    "2017-06-29 00:00:00", "hücuma başlayın")
        testExtract("Cümə axşamı saat 05:00 da hücuma başlayın",
                    "2017-06-29 05:00:00", "hücuma başlayın")
        testExtract("4 il sonra oyanmağı xatırlat",
                    "2021-06-27 00:00:00", "oyanmağı xatırlat")
        testExtract("4 il 4 gündə oyanmağı xatırlat",
                    "2021-07-01 00:00:00", "oyanmağı xatırlat")
        testExtract("dekabr 3",
                    "2017-12-03 00:00:00", "")
        testExtract("bu axşam saat 8:00 da görüşək",
                    "2017-06-27 20:00:00", "görüşək")
        testExtract("axşam 5 də görüşək ",
                    "2017-06-27 17:00:00", "görüşək")
        testExtract("səhər 8 də görüşək",
                    "2017-06-28 08:00:00", "görüşək")
        testExtract("mənə səhər 8 də oyanmağı xatırlat",
                    "2017-06-28 08:00:00", "mənə oyanmağı xatırlat")
        testExtract("çərşənbə axşamı hava necədir",
                    "2017-06-27 00:00:00", "hava necədir")
        testExtract("bazar ertəsi hava necədir",
                    "2017-07-03 00:00:00", "hava necədir")
        testExtract("bu çərşənbə günü hava necədir",
                    "2017-06-28 00:00:00", "hava necədir")
        testExtract("keçən bazar ertəsi hava necə idi",
                    "2017-06-26 00:00:00", "hava necə idi")
        testExtract("5 iyun 2017 ci il axşamı anama zəng etməyi xatırlat",
                    "2017-06-05 19:00:00", "anama zəng etməyi xatırlat")
        testExtract("dünən hansı gün idi",
                    "2017-06-26 00:00:00", "hansı gün idi")
        testExtract("dünən 6 da şam yedim",
                    "2017-06-26 06:00:00", "şam yedim")
        testExtract("dünən səhər 6 da şam yedim",
                    "2017-06-26 06:00:00", "şam yedim")
        testExtract("dünən axşam 6 da şam yedim",
                    "2017-06-26 18:00:00", "şam yedim")

    def test_extract_relativedatetime_az(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("5 dəqiqəyə görüşək",
                    "2017-06-27 10:06:02", "görüşək")
        testExtract("5 saniyədə görüşək",
                    "2017-06-27 10:01:07", "görüşək")
        testExtract("1 saatda görüşək",
                    "2017-06-27 11:01:02", "görüşək")
        testExtract("2 saata görüşək",
                    "2017-06-27 12:01:02", "görüşək")

    def test_spaces(self):
        self.assertEqual(normalize("   bu  sınaqdır"),
                         "bu sınaqdır")
        self.assertEqual(normalize("   bu    bir   sınaqdır"),
                         "bu 1 sınaqdır")

    def test_numbers(self):
        self.assertEqual(normalize("bu bir iki üç sınaqdır"),
                         "bu 1 2 3 sınaqdır")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("bu bir iki üç sınaqdır"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("bu on bir on iki on üç sınaqdır"),
                         [11.0, 12.0, 13.0])
        self.assertEqual(extract_numbers("bu bir iyirmi bir sınaqdır"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 it, yeddi donuz, mənim dostum var "
                                         "3 dəfə 5 macarena"),
                         [1, 7, 3, 5])
        self.assertEqual(extract_numbers("iki pivə iki ayıa"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("iyirmi 20 iyirmi"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("iyirmi 20 22"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("iyirmi iyirmi iki iyirmi"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("iyirmi 2"),
                         [22.0])
        self.assertEqual(extract_numbers("iyirmi 20 iyirmi 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("üçdəbir bir"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("altı trilyon", short_scale=True),
                         [6e12])
        self.assertEqual(extract_numbers("altı trilyon", short_scale=False),
                         [6e18])
        self.assertEqual(extract_numbers("iki donuz və altı trilyon bakteriya",
                                         short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("iki donuz altı trilyon bakteriya",
                                         short_scale=False), [2, 6e18])
        self.assertEqual(extract_numbers("otuz ikinci ya birinci",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("bu yeddi səkkiz doqquz yarım sınaqdır"),
                         [7.0, 8.0, 9.5])


if __name__ == "__main__":
    unittest.main()
