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
from lingua_franca.time import default_timezone
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import normalize


def setUpModule():
    load_language("pl-pl")
    set_default_lang("pl")


def tearDownModule():
    unload_language("cs")


class TestNormalize(unittest.TestCase):
    def test_extract_number(self):
        self.assertEqual(extract_number('to jest pół testu'), 0.5)
        self.assertEqual(extract_number("to jest pierwszy test",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("to jest 2 test"), 2)
        self.assertEqual(extract_number("to jest drugi test",
                                        ordinals=True), 2)
        self.assertEqual(extract_number("to jest trzeci test",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("czwarty test",
                                        ordinals=True), 4.0)
        self.assertEqual(extract_number("trzydziesty szósty test",
                                        ordinals=True), 36.0)
        self.assertEqual(extract_number("to jest test numer 4"), 4)
        self.assertEqual(extract_number("jedna trzecia szklanki"), 1.0 / 3.0)
        self.assertEqual(extract_number("trzy szklanki"), 3)
        self.assertEqual(extract_number("1/3 szklanki"), 1.0 / 3.0)
        self.assertEqual(extract_number("jedna czwarta szklanki"), 0.25)
        self.assertEqual(extract_number("1/4 szklanki"), 0.25)
        self.assertEqual(extract_number("jedna czwarta szklanki"), 0.25)
        self.assertEqual(extract_number("2/3 szklanki"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 szklanki"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 i 3/4 szklanki"), 1.75)
        self.assertEqual(extract_number("1 szklanka i jedna druga"), 1.5)
        self.assertEqual(extract_number("jedna szklanka i jedna druga"), 1.5)
        self.assertEqual(extract_number("jeden i jedna druga szklanki"), 1.5)
        self.assertEqual(extract_number("trzy czwarte szklanki"), 3.0 / 4.0)
        self.assertEqual(extract_number("dwadzieścia dwa"), 22)
        self.assertEqual(extract_number("Dwadzieścia dwa i trzy piąte"), 22.6)
        self.assertEqual(extract_number("dwieście"), 200)
        self.assertEqual(extract_number("dziewięć tysięcy"), 9000)
        self.assertEqual(extract_number("sześćset sześćdziesiąt sześć"), 666)
        self.assertEqual(extract_number("dwa miliony"), 2000000)
        self.assertEqual(extract_number("dwa miliony pięćset tysięcy "
                                        "ton metalu"), 2500000)
        self.assertEqual(extract_number("sześć bilionów"), 6000000000000.0)
        self.assertEqual(extract_number("jeden przecinek pięć"), 1.5)
        self.assertEqual(extract_number("trzy kropka czternaście"), 3.14)
        self.assertEqual(extract_number("zero przecinek dwa"), 0.2)
        self.assertEqual(extract_number("miliardy lat starsze"),
                         1000000000.0)
        self.assertEqual(extract_number("sto tysięcy"), 100000)
        self.assertEqual(extract_number("minus 2"), -2)
        self.assertEqual(extract_number("ujemne siedemdziesiąt"), -70)
        self.assertEqual(extract_number("tysiąc milionów"), 1000000000)
        self.assertEqual(extract_number("sześć trzecich"),
                         6 / 3)
        self.assertEqual(extract_number("trzydzieści sekund"), 30)
        self.assertEqual(extract_number("to jest miliardowy test",
                                        ordinals=True), 1e09)
        self.assertEqual(extract_number("to jest miliardowa część"), 1e-9)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("dwadzieścia tysięcy"), 20000)
        self.assertEqual(extract_number("pięćdziesiąt milionów"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("trzysta dwadzieścia miliardów trzysta milionów \
                                        dziewięćset pięćdziesiąt tysięcy sześćset \
                                        siedemdziesiąt pięć kropka osiem"),
                         320300950675.8)
        self.assertEqual(extract_number("dziewięćset dziewięćdziesiąt dziewięć milionów \
                                        dziewięćset dziewięćdziesiąt dziewięć tysięcy \
                                        dziewięćset dziewięćdziesiąt dziewięć przecinek dziewięć"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("osiemset bilionów dwieście \
                                        pięćdziesiąt siedem"), 800000000000257.0)

        self.assertTrue(extract_number("Szybki gracz") is False)
        self.assertTrue(extract_number("krejzi") is False)

        self.assertTrue(extract_number("krejzi zero") is not False)
        self.assertEqual(extract_number("krejzi zero"), 0)

        self.assertTrue(extract_number("super 0") is not False)
        self.assertEqual(extract_number("super 0"), 0)

        self.assertEqual(extract_number(
            "jesteś drugi", ordinals=True), 2)
        self.assertEqual(extract_number("całkowicie 100%"), 100)

    def test_extract_duration_pl(self):
        self.assertEqual(extract_duration("10 sekund"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 minut"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 godziny"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 dni"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 tygodni"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("siedem godzin"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 sekundy"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("osiem i pół dnia trzydzieści dziewięć sekund",
                                          lang='pl-pl'),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("Ustaw stoper na 30 minut"),
                         (timedelta(minutes=30), "ustaw stoper na"))
        self.assertEqual(extract_duration("Cztery i pół minuty do zachodu"),
                         (timedelta(minutes=4.5), "do zachodu"))
        self.assertEqual(extract_duration("dziewiętnaście minut po pełnej godzinie"),
                         (timedelta(minutes=19), "po pełnej godzinie"))
        self.assertEqual(extract_duration("obudź mnie za 3 tygodnie, czterysta dziewięćdziesiąt siedem dni i"
                                          " trzysta 91.6 sekund"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "obudź mnie za ,  i"))
        self.assertEqual(extract_duration("ten film trwa jedną godzinę, pięćdziesiąt siedem i pół minuty",
                                          lang='pl-pl'),
                         (timedelta(hours=1, minutes=57.5),
                             "ten film trwa ,"))
        self.assertEqual(extract_duration("10-sekund"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-minut"),
                         (timedelta(minutes=5), ""))

    def test_extractdatetime_pl(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            print(text) # TODO Remove me
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("teraz jest czas",
                    "2017-06-27 13:04:00", "jest czas")
        testExtract("za sekundę",
                    "2017-06-27 13:04:01", "")
        testExtract("za minutę",
                    "2017-06-27 13:05:00", "")
        testExtract("następna dekada",
                    "2027-06-27 00:00:00", "")
        testExtract("za jeden wiek",
                    "2117-06-27 00:00:00", "")
        testExtract("za jedno milenium",
                    "3017-06-27 00:00:00", "")
        testExtract("za 5 dekad",
                    "2067-06-27 00:00:00", "")
        testExtract("za 2 wieki",
                    "2217-06-27 00:00:00", "")
        testExtract("za godzinę",
                    "2017-06-27 14:04:00", "")
        testExtract("chcę to do godziny",
                    "2017-06-27 14:04:00", "chcę to")
        testExtract("za 1 sekundę",
                    "2017-06-27 13:04:01", "")
        testExtract("za 2 sekundy",
                    "2017-06-27 13:04:02", "")
        testExtract("Nastaw zasadzkę na za minutę",
                    "2017-06-27 13:05:00", "nastaw zasadzkę")
        testExtract("Nastaw zasadzkę na pół godziny",
                    "2017-06-27 13:34:00", "nastaw zasadzkę")
        testExtract("Nastaw zasadzkę za 5 dni od dzisiaj",
                    "2017-07-02 00:00:00", "nastaw zasadzkę")
        testExtract("pojutrze",
                    "2017-06-29 00:00:00", "")
        testExtract("Jaka będzie pogoda pojutrze?",
                    "2017-06-29 00:00:00", "jaka będzie pogoda")
        testExtract("Przypomnij mi o 10:45 po południu",
                    "2017-06-27 22:45:00", "przypomnij mi")
        testExtract("Jaka będzie pogoda w piątek rano",
                    "2017-06-30 08:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda jutro",
                    "2017-06-28 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda dzisiaj po południu",
                    "2017-06-27 15:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda dzisiaj wieczorem?",
                    "2017-06-27 19:00:00", "jaka będzie pogoda")
        testExtract("jaka była pogoda dzisiaj rano",
                    "2017-06-27 08:00:00", "jaka była pogoda")
        testExtract("przypomnij mi bym zadzwonił do mamy za 8 tygodni i 2 dni",
                    "2017-08-24 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy 3 Sierpnia",
                    "2017-08-03 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy jutro o 7 rano",
                    "2017-06-28 07:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi jutro bym zadzwonił do mamy o 9 w nocy",
                    "2017-06-28 21:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi jutro bym zadzwonił do mamy o 7 rano",
                    "2017-06-28 07:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za godzinę",
                    "2017-06-27 14:04:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 1730",
                    "2017-06-27 17:30:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 0630",
                    "2017-06-28 06:30:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 7",
                    "2017-06-27 19:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy w czwartek o 7 wieczorem",
                    "2017-06-29 19:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy w Czwartek o 7 rano",
                    "2017-06-29 07:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 7 rano w Czwartek",
                    "2017-06-29 07:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 2 godziny",
                    "2017-06-27 15:04:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 15 minut",
                    "2017-06-27 13:19:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za piętnaście minut",
                    "2017-06-27 13:19:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za pół godziny",
                    "2017-06-27 13:34:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 10 rano 2 dni po Sobocie",
                    "2017-07-03 10:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Zagraj Rick Astley za 2 dni po Piątku",
                    "2017-07-02 00:00:00", "zagraj rick astley")
        testExtract("Zacznij inwazję o 3:45 po południu",
                    "2017-06-27 15:45:00", "zacznij inwazję")
        testExtract("W poniedziałek, zamów ciasto z piekarni",
                    "2017-07-03 00:00:00", "zamów ciasto z piekarni")
        testExtract("Zagraj Wszystkiego Najlepszego za 5 lat od dzisiaj",
                    "2022-06-27 00:00:00", "zagraj wszystkiego najlepszego")
        testExtract("Skype z Mamą o 12:45 w następny Czwartek",
                    "2017-07-06 12:45:00", "skype z mamą")
        testExtract("Jaka będzie pogoda w następny Piątek",
                    "2017-06-30 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w następną Środę",
                    "2017-07-05 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w następny Czwartek",
                    "2017-07-06 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w następny piątek rano",
                    "2017-06-30 08:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w następny Piątek wieczorem",
                    "2017-06-30 19:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w następny Piątek po południu",
                    "2017-06-30 15:00:00", "jaka będzie pogoda")
        testExtract("Przypomnij mi bym zadzwonił do mamy 3 Sierpnia",
                    "2017-08-03 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Kup fajerwerki 4 Lipca",
                    "2017-07-04 00:00:00", "kup fajerwerki")
        testExtract("Jaka będzie pogoda za 2 tygodnie po następnym Piątku",
                    "2017-07-14 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w Środę o 7 rano",
                    "2017-06-28 07:00:00", "jaka będzie pogoda")
        testExtract("Ustaw spotkanie na 12:45 w następny Czwartek",
                    "2017-07-06 12:45:00", "ustaw spotkanie")
        testExtract("Jaka będzie pogoda w ten Czwartek",
                    "2017-06-29 00:00:00", "jaka będzie pogoda")
        testExtract("Ustaw wizytę na za 2 tygodnie i 6 dni od Soboty",
                    "2017-07-21 00:00:00", "ustaw wizytę na")
        testExtract("Zacznij inwazję o 03 45 w Czwartek",
                    "2017-06-29 03:45:00", "zacznij inwazję")
        testExtract("Zacznij inwazję o 8 wieczorem w Czwartek",
                    "2017-06-29 20:00:00", "zacznij inwazję")
        testExtract("Zacznij inwazję w Czwartek południe",
                    "2017-06-29 12:00:00", "zacznij inwazję")
        testExtract("Zacznij inwazję w Czwartek o północy",
                    "2017-06-29 00:00:00", "zacznij inwazję")
        testExtract("Przypomnij mi bym się obudził za 4 lata",
                    "2021-06-27 00:00:00", "przypomnij mi bym się obudził")
        testExtract("Przypomnij mi bym się obudził za 4 lata i 4 dni",
                    "2021-07-01 00:00:00", "przypomnij mi bym się obudził")
        testExtract("Jaka będzie pogoda za 3 dni od jutra",
                    "2017-07-01 00:00:00", "jaka będzie pogoda")
        testExtract("grudzień trzeci",
                    "2017-12-03 00:00:00", "")
        testExtract("Spotkajmy się o 8 wieczorem",
                    "2017-06-27 20:00:00", "spotkajmy się")
        testExtract("Spotkajmy się o 5 po południu",
                    "2017-06-27 17:00:00", "spotkajmy się")
        testExtract("Spotkajmy się o 8 rano",
                    "2017-06-28 08:00:00", "spotkajmy się")
        testExtract("Przypomnij mi bym się obudził o 8 rano",
                    "2017-06-28 08:00:00", "przypomnij mi bym się obudził")
        testExtract("Jaka będzie pogoda we Wtorek",
                    "2017-06-27 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w Poniedziałek",
                    "2017-07-03 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka będzie pogoda w środę",
                    "2017-06-28 00:00:00", "jaka będzie pogoda")
        testExtract("w Czwartek jaka będzie pogoda",
                    "2017-06-29 00:00:00", "jaka będzie pogoda")
        testExtract("w ten Czwartek jaka będzie pogoda",
                    "2017-06-29 00:00:00", "jaka będzie pogoda")
        testExtract("Jaka była pogoda w ostatni Poniedziałek",
                    "2017-06-26 00:00:00", "jaka była pogoda")
        testExtract("Ustaw alarm na Środę 8 wieczór",
                    "2017-06-28 20:00:00", "ustaw alarm")
        testExtract("Ustaw alarm na Środę o trzeciej po południu",
                    "2017-06-28 15:00:00", "ustaw alarm")
        testExtract("Ustaw alarm na Środę o 3 rano",
                    "2017-06-28 03:00:00", "ustaw alarm")
        testExtract("Ustaw alarm na 7:00 wieczorem",
                    "2017-06-27 19:00:00", "ustaw alarm")
        testExtract("5 czerwca 2017 wieczorem przypomnij mi bym" +
                    " zadzwonił do mamy",
                    "2017-06-05 19:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("dodaj do mojego kalendarza poranne spotkanie z Juliuszem" +
                    " czwartego Marca",
                    "2018-03-04 08:00:00",
                    "dodaj do mojego kalendarza spotkanie z juliuszem")
        testExtract("Przypomnij mi bym zadzwonił do mamy w następny Wtorek",
                    "2017-07-04 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 3 tygodnie",
                    "2017-07-18 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 8 tygodni",
                    "2017-08-22 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 8 tygodni i 2 dni",
                    "2017-08-24 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 4 dni",
                    "2017-07-01 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 3 miesiące",
                    "2017-09-27 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy za 2 lata i 2 dni",
                    "2019-06-29 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy w następnym tygodniu",
                    "2017-07-04 00:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 10 rano w Sobotę",
                    "2017-07-01 10:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 10 rano w tę Sobotę",
                    "2017-07-01 10:00:00", "przypomnij mi bym zadzwonił do mamy")
        testExtract("Przypomnij mi bym zadzwonił do mamy o 10 w następną Sobotę",
                    "2017-07-01 10:00:00", "przypomnij mi bym zadzwonił do mamy")
        # test yesterday
        testExtract("Jaki dzień był wczoraj",
                    "2017-06-26 00:00:00", "jaki dzień był")
        testExtract("Jaki dzień był przedwczoraj",
                    "2017-06-25 00:00:00", "jaki dzień był")
        testExtract("Miałem kolację wczoraj o 6",
                    "2017-06-26 06:00:00", "miałem kolację")
        testExtract("Miałem kolację wczoraj o 6 rano",
                    "2017-06-26 06:00:00", "miałem kolację")
        testExtract("Miałem kolację wczoraj o 6 wieczorem",
                    "2017-06-26 18:00:00", "miałem kolację")

        # Below two tests, ensure that time is picked
        # even if no am/pm is specified
        # in case of weekdays/tonight
        # TODO imperfect as leaves "dzień robocze", but calculates time correctly
        testExtract("Nastaw alarm na 9 w dni robocze",
                    "2017-06-27 21:00:00", "nastaw alarm dzień robocze")
        testExtract("na 8 wieczorem",
                    "2017-06-27 20:00:00", "")
        testExtract("na 8:30 wieczorem",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("nastaw alarm na 9:30 wieczorem",
                    "2017-06-27 21:30:00", "nastaw alarm")
        testExtract("nastaw alarm na 9:00 wieczorem",
                    "2017-06-27 21:00:00", "nastaw alarm")
        # Check if it picks the intent irrespective of correctness
        testExtract("przypomnij mi o grze dzisiaj o 11:30 wieczorem",
                    "2017-06-27 23:30:00", "przypomnij mi o grze")
        testExtract("ustaw alarm na 7:30 w dni robocze",
                    "2017-06-27 19:30:00", "ustaw alarm w dzień robocze")

        #  "# days <from X/after X>"
        testExtract("moje urodziny są za 2 dni",
                    "2017-06-29 00:00:00", "moje urodziny są")
        testExtract("moje urodziny są za 2 dni od dzisiaj",
                    "2017-06-29 00:00:00", "moje urodziny są")
        testExtract("moje urodziny są za 2 dni od jutra",
                    "2017-06-30 00:00:00", "moje urodziny są")
        testExtract("moje urodziny są 2 dni po jutrze",
                    "2017-06-30 00:00:00", "moje urodziny są")
        testExtract("przypomnij mi żebym zadzwonił do mamy o 10 rano 2 dni po następnej Sobocie",
                    "2017-07-10 10:00:00", "przypomnij mi żebym zadzwonił do mamy")
        testExtract("moje urodziny są za 2 dni od wczoraj",
                    "2017-06-28 00:00:00", "moje urodziny są")

        #  "# days ago>"
        testExtract("moje urodziny były 1 dzień temu",
                    "2017-06-26 00:00:00", "moje urodziny były")
        testExtract("moje urodziny były 2 dni temu",
                    "2017-06-25 00:00:00", "moje urodziny były")
        testExtract("moje urodziny były 3 dni temu",
                    "2017-06-24 00:00:00", "moje urodziny były")
        testExtract("moje urodziny były 4 dni temu",
                    "2017-06-23 00:00:00", "moje urodziny były")
        testExtract("spotkajmy się w nocy",
                    "2017-06-27 22:00:00", "spotkajmy się")
        testExtract("jaka będzie pogoda jutro w nocy",
                    "2017-06-28 22:00:00", "jaka będzie pogoda")
        testExtract("jaka będzie pogoda w następny Wtorek nocy",
                    "2017-07-04 22:00:00", "jaka będzie pogoda")

    def test_extract_ambiguous_time_pl(self):
        morning = datetime(2017, 6, 27, 8, 1, 2)
        evening = datetime(2017, 6, 27, 20, 1, 2)
        noonish = datetime(2017, 6, 27, 12, 1, 2)
        self.assertEqual(
            extract_datetime('nakarm rybę'), None)
        self.assertEqual(
            extract_datetime('dzień'), None)
        self.assertEqual(
            extract_datetime('tydzień'), None)
        self.assertEqual(
            extract_datetime('miesiąc'), None)
        self.assertEqual(
            extract_datetime('rok'), None)
        self.assertEqual(
            extract_datetime(' '), None)

    def test_extract_relativedatetime_pl(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("spotkajmy się za 5 minut",
                    "2017-06-27 10:06:02", "spotkajmy się")
        testExtract("spotkajmy się za 5minut",
                    "2017-06-27 10:06:02", "spotkajmy się")
        testExtract("spotkajmy się za 5 sekund",
                    "2017-06-27 10:01:07", "spotkajmy się")
        testExtract("spotkajmy się za 1 godzinę",
                    "2017-06-27 11:01:02", "spotkajmy się")
        testExtract("spotkajmy się za 2 godziny",
                    "2017-06-27 12:01:02", "spotkajmy się")
        testExtract("spotkajmy się za 2godziny",
                    "2017-06-27 12:01:02", "spotkajmy się")
        testExtract("spotkajmy się za 1 minutę",
                    "2017-06-27 10:02:02", "spotkajmy się")
        testExtract("spotkajmy się za 1 sekundę",
                    "2017-06-27 10:01:03", "spotkajmy się")
        testExtract("spotkajmy się za 5sekund",
                    "2017-06-27 10:01:07", "spotkajmy się")

    def test_spaces(self):
        self.assertEqual(normalize("  to   jest    test"),
                         "to jest test")
        self.assertEqual(normalize("  to   jest    test  "),
                         "to jest test")
        self.assertEqual(normalize("  to   jest  jeden    test"),
                         "to jest 1 test")

    def test_numbers(self):
        self.assertEqual(normalize("to jest jeden dwa trzy  test"),
                         "to jest 1 2 3 test")
        self.assertEqual(normalize("  to jest cztery pięć sześć  test"),
                         "to jest 4 5 6 test")
        self.assertEqual(normalize("to jest dziesięć jedenaście dwanaście test"),
                         "to jest 10 11 12 test")
        self.assertEqual(normalize("to jest osiemnaście dziewiętnaście dwadzieścia"),
                         "to jest 18 19 20")
        self.assertEqual(normalize("to jest jeden dziewiętnaście dwadzieścia dwa"),
                         "to jest 1 19 20 2")
        self.assertEqual(normalize("to jest jeden dwa dwadzieścia dwa"),
                         "to jest 1 2 20 2")
        self.assertEqual(normalize("to jest jeden i pół"),
                         "to jest 1 pół")
        self.assertEqual(normalize("to jest jeden i pół i pięć sześć"),
                         "to jest 1 pół 5 6")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("to jest jeden dwa trzy  test"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("to jest cztery pięć sześć  test"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("to jest dziesięć jedenaście dwanaście  test"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("to jest jeden dwadzieścia jeden  test"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("1 pies, siedem świń, macdonald miał "
                                         "farmę, 3 razy 5 macarena"),
                         [1, 7, 3, 5])
        self.assertEqual(extract_numbers("dwa piwa dwa wina"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("dwadzieścia 20 dwadzieścia"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("dwadzieścia 20 22"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("dwadzieścia dwadzieścia dwa dwadzieścia"),
                         [20.0, 22.0, 20.0])
        self.assertEqual(extract_numbers("dwadzieścia 2"),
                         [22.0])
        self.assertEqual(extract_numbers("dwadzieścia 20 dwadzieścia 2"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("jedna trzecia jeden"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("trzeci", ordinals=True), [3])
        self.assertEqual(extract_numbers("sześć trylionów"),
                         [6e18])
        self.assertEqual(extract_numbers("dwie świnie i sześć bilionów bakterii",
                                         lang='pl-pl'), [2, 6e12])
        self.assertEqual(extract_numbers("trzydziesty drugi lub pierwszy",
                                         ordinals=True), [32, 1])
        self.assertEqual(extract_numbers("to jest siedem osiem dziewięć i"
                                         " pół test"),
                         [7.0, 8.0, 9.5])


if __name__ == "__main__":
    unittest.main()
