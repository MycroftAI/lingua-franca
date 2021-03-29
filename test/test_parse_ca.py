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
from datetime import datetime, time

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.parse import get_gender
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_number
from lingua_franca.parse import normalize
from lingua_franca.time import default_timezone


def setUpModule():
    load_language('ca-es')
    set_default_lang('ca')


def tearDownModule():
    unload_language('ca')


class TestNormalize(unittest.TestCase):
    """
        Test cases for Catalan parsing
    """

    def test_articles_ca(self):
        self.assertEqual(normalize("aquesta és la prova",
                                   lang="ca", remove_articles=True),
                         "és prova")
        self.assertEqual(
            normalize("això és una frase", lang="ca", remove_articles=True),
            "això és 1 frase")
        self.assertEqual(
            normalize("i una altra prova", lang="ca", remove_articles=True),
            "1 altra prova")
        self.assertEqual(normalize("això és un test extra",
                                   lang="ca",
                                   remove_articles=False), "això és 1 test extra")

    def test_extractnumber_ca(self):
        self.assertEqual(extract_number("aquest és el primer intent", lang="ca"),
                         1)
        self.assertEqual(extract_number("i aquesta la segona prova", lang="ca"), 2)
        self.assertEqual(extract_number("això l'intent 2", lang="ca"),
                         2)
        self.assertEqual(extract_number("això és un terç de pizza",
                                        lang="ca"), 1.0 / 3.0)
        self.assertEqual(extract_number("axiò és la prova del número quatre",
                                        lang="ca"), 4)
        self.assertEqual(extract_number("un terç de tassa", lang="ca"),
                         1.0 / 3.0)
        self.assertEqual(extract_number("3 tasses", lang="ca"), 3)
        self.assertEqual(extract_number("1/3 tassa", lang="ca"), 1.0 / 3.0)
        self.assertEqual(extract_number("quart d'hora", lang="ca"), 0.25)
        self.assertEqual(extract_number("1/4 hora", lang="ca"), 0.25)
        self.assertEqual(extract_number("un quart d'hora", lang="ca"), 0.25)
        self.assertEqual(extract_number("2/3 pinga", lang="ca"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 pinga", lang="ca"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 i 3/4 cafè", lang="ca"), 1.75)
        self.assertEqual(extract_number("1 cafè i mig", lang="ca"), 1.5)
        self.assertEqual(extract_number("un cafè i un mig", lang="ca"), 1.5)
        self.assertEqual(
            extract_number("tres quarts de xocolata", lang="ca"),
            3.0 / 4.0)
        self.assertEqual(
            extract_number("Tres quarts de xocolate", lang="ca"),
            3.0 / 4.0)
        self.assertEqual(extract_number("tres quart de xocolata",
                                        lang="ca"), 3.0 / 4.0)
        self.assertEqual(extract_number("set coma cinc", lang="ca"), 7.5)
        self.assertEqual(extract_number("set coma 5", lang="ca"), 7.5)
        self.assertEqual(extract_number("set i mig", lang="ca"), 7.5)
        self.assertEqual(extract_number("set amb vuitanta", lang="ca"), 7.80)
        self.assertEqual(extract_number("set i vuit", lang="ca"), 7.8)
        self.assertEqual(extract_number("set coma zero vuit",
                                        lang="ca"), 7.08)
        self.assertEqual(extract_number("set coma zero zero vuit",
                                        lang="ca"), 7.008)
        self.assertEqual(extract_number("vint trenta ens", lang="ca"),
                         20.0 / 30.0)
        self.assertEqual(extract_number("dos", lang="ca"), 2)
        self.assertEqual(extract_number("dues", lang="ca"), 2)
        self.assertEqual(extract_number("tres", lang="ca"), 3)
        self.assertEqual(extract_number("quatre", lang="ca"), 4)
        self.assertEqual(extract_number("deu", lang="ca"), 10)
        self.assertEqual(extract_number("trenta-cinc", lang="ca"), 35)
        self.assertEqual(extract_number("seixanta-sis", lang="ca"), 66)
        self.assertEqual(extract_number("vint-i-dues", lang="ca"), 22)
        self.assertEqual(extract_number("vint-i-dos", lang="ca"), 22)
        self.assertEqual(extract_number("quatre-centes", lang="ca"), 400)
        self.assertEqual(extract_number("cinc-cents", lang="ca"), 500)
        self.assertEqual(extract_number("sis coma sis-cents seixanta",
                                        lang="ca"), 6.66)
        self.assertEqual(extract_number("sis-cents seixanta-sis",
                                        lang="ca"), 666)
        self.assertEqual(extract_number("sis-cents punt zero sis",
                                        lang="ca"), 600.06)
        self.assertEqual(extract_number("sis-cents coma zero zero sis",
                                        lang="ca"), 600.006)
        self.assertEqual(extract_number("tres-cents coma zero zero tres",
                                        lang="ca"), 300.003)

    def test_agressive_pruning_ca(self):
        self.assertEqual(normalize("una paraula", lang="ca"),
                         "1 paraula")
        self.assertEqual(normalize("un mot", lang="ca"),
                         "1 mot")
        self.assertEqual(normalize("aquesta paraula u", lang="ca"),
                         "paraula 1")
        self.assertEqual(normalize("l'home el va pegar", lang="ca"),
                         "l'home va pegar")
        self.assertEqual(normalize("qui va equivocar-se aquell dia", lang="ca"),
                         "qui va equivocar-se dia")

    def test_spaces_ca(self):
        self.assertEqual(normalize("  això   és  el    test", lang="ca"),
                         "això és test")
        self.assertEqual(normalize("  això   és  l'intent", lang="ca"),
                         "això és l'intent")
        self.assertEqual(normalize("  això   són les    proves  ", lang="ca"),
                         "això són proves")
        self.assertEqual(normalize("  això   és  un    test", lang="ca",
                                   remove_articles=False),
                         "això és 1 test")

    def test_numbers_ca(self):
        self.assertEqual(normalize("això és el test un dos tres", lang="ca"),
                         "això és test 1 2 3")
        self.assertEqual(normalize("és una prova set vuit nou   huit", lang="ca"),
                         "és 1 prova 7 8 9 8")
        self.assertEqual(
            normalize("prova zero deu onze dotze tretze", lang="ca"),
            "prova 0 10 11 12 13")
        #TODO: seixanta-sis > 66
        #self.assertEqual(
        #    normalize("prova 1000 600 seixanta-sis", lang="ca",
        #              remove_articles=False),
        #    "prova 1000 600 66")
        #TODO: mil dotze > 1012
        #self.assertEqual(
        #    normalize("prova mil dotze", lang="ca",
        #              remove_articles=False),
        #    "prova 1012")
        #TODO: dues-centes vint-i-quatre > 224
        #self.assertEqual(
        #    normalize("prova dues-centes vint-i-quatre", lang="ca",
        #              remove_articles=False),
        #    "prova 224")

        self.assertEqual(
            normalize("test set i mig", lang="ca",
                      remove_articles=False),
            "test 7 mig")
        self.assertEqual(
            normalize("test dos punt nou", lang="ca"),
            "test 2 punt 9")
        self.assertEqual(
            normalize("test cent i nou", lang="ca",
                      remove_articles=False),
            "test 100 9")
        self.assertEqual(
            normalize("test vint i 1", lang="ca"),
            "test 20 1")

    def test_extractdatetime_ca(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="ca")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract("quin dia és avui",
                    "2017-06-27 00:00:00", "dia")
        testExtract("quin dia som avui",
                    "2017-06-27 00:00:00", "dia")
        testExtract("quin dia és demà",
                    "2017-06-28 00:00:00", "dia")
        testExtract("quin dia va ser ahir",
                    "2017-06-26 00:00:00", "dia ser")
        testExtract("quin dia va ser abans ahir",
                    "2017-06-25 00:00:00", "dia ser")
        testExtract("quin dia va ser abans d'ahir",
                    "2017-06-25 00:00:00", "dia ser")
        testExtract("quin dia va ser abans-d'ahir",
                    "2017-06-25 00:00:00", "dia ser")
        testExtract("quin dia va ser abans d'abans d'ahir",
                    "2017-06-24 00:00:00", "dia ser")
        testExtract("fer el sopar d'aquí 5 dies",
                    "2017-07-02 00:00:00", "fer sopar aquí")
        testExtract("fer el sopar en 5 dies",
                    "2017-07-02 00:00:00", "fer sopar")
        testExtract("quin temps farà demà?",
                    "2017-06-28 00:00:00", "temps farà")
        testExtract("quin temps farà demà-passat?",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("quin temps farà despús-demà?",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("quin temps farà despús demà?",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("truca a la mare les 10:45 pm",
                    "2017-06-27 22:45:00", "truca mare")
        testExtract("quin temps fa el divendres de matí",
                    "2017-06-30 08:00:00", "temps fa")
        testExtract("truca'm per a quedar d'aquí a 8 setmanes i 2 dies",
                    "2017-08-24 00:00:00", "truca m quedar aquí i")
        testExtract("Toca black-metal 2 dies després de divendres",
                    "2017-07-02 00:00:00", "toca black-metal")
        testExtract("Toca satanic black metal 2 dies per a aquest divendres",
                    "2017-07-02 00:00:00", "toca satanic black metal")
        testExtract("Toca super black metal 2 dies a partir d'aquest divendres",
                    "2017-07-02 00:00:00", "toca super black metal")
        testExtract("Começa la invasió a les 3:45 pm de dijous",
                    "2017-06-29 15:45:00", "começa invasió")
        testExtract("dilluns, compra formatge",
                    "2017-07-03 00:00:00", "compra formatge")
        testExtract("Envia felicitacions d'aquí a 5 anys",
                    "2022-06-27 00:00:00", "envia felicitacions aquí")
        testExtract("Envia felicitacions en 5 anys",
                    "2022-06-27 00:00:00", "envia felicitacions")
        testExtract("Truca per Skype a la mare pròxim dijous a les 12:45 pm",
                    "2017-06-29 12:45:00", "truca skype mare")
        testExtract("quin temps fa aquest divendres?",
                    "2017-06-30 00:00:00", "temps fa")
        testExtract("quin temps fa aquest divendres per la tarda?",
                    "2017-06-30 15:00:00", "temps fa")
        testExtract("quin temps farà aquest divendres de matinada?",
                    "2017-06-30 04:00:00", "temps farà")
        testExtract("quin temps fa aquest divendres a mitja nit?",
                    "2017-06-30 00:00:00", "temps fa mitjanit")
        testExtract("quin temps fa aquest divendres al migdia?",
                    "2017-06-30 12:00:00", "temps fa")
        testExtract("quin temps fa aquest divendres al final de tarda?",
                    "2017-06-30 19:00:00", "temps fa")
        testExtract("quin temps fa aquest divendres a mig matí?",
                    "2017-06-30 10:00:00", "temps fa")
        testExtract("recorda de trucar a la mare el dia 3 d'agost",
                    "2017-08-03 00:00:00", "recorda trucar mare")

        testExtract("compra ganivets el 13 de maig",
                    "2018-05-13 00:00:00", "compra ganivets")
        testExtract("gasta diners el dia 13 de maig",
                    "2018-05-13 00:00:00", "gasta diners")
        testExtract("compra espelmes el 13 de maig",
                    "2018-05-13 00:00:00", "compra espelmes")
        testExtract("beure cervesa el 13 de maig",
                    "2018-05-13 00:00:00", "beure cervesa")
        testExtract("quin temps farà 1 dia després de demà",
                    "2017-06-29 00:00:00", "temps farà")
        testExtract("quin temps farà a les 0700 hores",
                    "2017-06-27 07:00:00", "temps farà")
        testExtract("quin temps farà demà a les 7 en punt",
                    "2017-06-28 07:00:00", "temps farà")
        testExtract("quin temps farà demà a les 2 de la tarda",
                    "2017-06-28 14:00:00", "temps farà")
        testExtract("quin temps farà demà a les 2",
                    "2017-06-28 02:00:00", "temps farà")
        testExtract("quin temps farà a les 2 de la tarda de divendres vinent",
                    "2017-06-30 14:00:00", "temps farà vinent")
        testExtract("recorda'm de despertar en 4 anys",
                    "2021-06-27 00:00:00", "recorda m despertar")
        testExtract("recorda'm de despertar en 4 anys i 4 dies",
                    "2021-07-01 00:00:00", "recorda m despertar i")
        #testExtract("dorm 3 dies després de demà",
        #            "2017-07-02 00:00:00", "dorm")
        testExtract("concerta cita d'aquí a 2 setmanes i 6 dies després de dissabte",
                    "2017-07-21 00:00:00", "concerta cita aquí i")
        testExtract("comença la festa a les 8 en punt de la nit de dijous",
                    "2017-06-29 20:00:00", "comença festa")

    def test_extractdatetime_default_ca(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime(
            'concerta cita per a 2 setmanes i 6 dies després de dissabte',
            anchor, lang='ca-es', default_time=default)
        self.assertEqual(default, res[0].time())


class TestExtractGender(unittest.TestCase):
    def test_gender_ca(self):
        # words with well defined grammatical gender rules
        self.assertEqual(get_gender("vaca", lang="ca"), "f")
        self.assertEqual(get_gender("cavall", lang="ca"), "m")
        self.assertEqual(get_gender("vaques", lang="ca"), "f")

        # words specifically defined in a lookup dictionary
        self.assertEqual(get_gender("home", lang="ca"), "m")
        self.assertEqual(get_gender("dona", lang="ca"), "f")
        self.assertEqual(get_gender("homes", lang="ca"), "m")
        self.assertEqual(get_gender("dones", lang="ca"), "f")

        # words where gender rules do not work but context does
        self.assertEqual(get_gender("bou", lang="ca"), None)
        self.assertEqual(get_gender("bou", "el bou menja herba", lang="ca"), "m")
        self.assertEqual(get_gender("home", "aquest home menja bous",
                                    lang="ca"), "m")
        self.assertEqual(get_gender("pont", lang="ca"), None)
        self.assertEqual(get_gender("pont", "aquest pont ha caigut",
                                    lang="ca"), "m")


if __name__ == "__main__":
    unittest.main()
