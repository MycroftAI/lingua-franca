# -*- coding: utf-8  -*-
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

from lingua_franca.parse import get_gender
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_number
from lingua_franca.parse import normalize


class TestNormalize(unittest.TestCase):
    """
        Test cases for Portuguese parsing
    """

    def test_articles_pt(self):
        self.assertEqual(normalize(u"isto é o teste",
                                   lang="pt", remove_articles=True),
                         u"isto teste")
        self.assertEqual(
            normalize(u"isto é a frase", lang="pt", remove_articles=True),
            u"isto frase")
        self.assertEqual(
            normalize("e outro teste", lang="pt", remove_articles=True),
            "outro teste")
        self.assertEqual(normalize(u"isto é o teste extra",
                                   lang="pt",
                                   remove_articles=False), u"isto e o teste"
                                                           u" extra")

    def test_extract_simple_numbers_pt(self):
        # simple number lookup
        self.assertEqual(extract_number("isto e o 2 teste", lang="pt"), 2)
        self.assertEqual(extract_number("3 canecos de cerveja", lang="pt"), 3)
        self.assertEqual(extract_number("isto e o teste numero 3", lang="pt"), 3)
        self.assertEqual(extract_number("isto e o teste numero um", lang="pt"), 1)
        self.assertEqual(extract_number("isto e o teste numero tres", lang="pt"), 3)
        self.assertEqual(extract_number("isto e o teste numero três", lang="pt"), 3)
        self.assertEqual(extract_number("isto e o teste numero quatro", lang="pt"), 4)
        self.assertEqual(extract_number("isto e o teste numero vinte", lang="pt"), 20)
        self.assertEqual(extract_number("isto e o teste numero mil", lang="pt"), 1000)

    def test_extract_fractional_numbers_pt(self):
        self.assertEqual(extract_number("isto e um terço de teste", lang="pt"), 1.0 / 3.0)
        self.assertEqual(extract_number("um terço de chavena", lang="pt"), 1.0 / 3.0)
        self.assertEqual(extract_number("1/3 de coisas", lang="pt"), 1.0 / 3.0)
        self.assertEqual(extract_number("quarto de hora", lang="pt"), 0.25)
        self.assertEqual(extract_number("1/4 hora", lang="pt"), 0.25)
        self.assertEqual(extract_number("um quarto hora", lang="pt"), 0.25)
        self.assertEqual(extract_number("2/3 pinga", lang="pt"), 2.0 / 3.0)
        self.assertEqual(extract_number("3/4 pinga", lang="pt"), 3.0 / 4.0)
        self.assertEqual(extract_number("1 e 3/4 cafe", lang="pt"), 1.75)
        self.assertEqual(extract_number("1 cafe e meio", lang="pt"), 1.5)
        self.assertEqual(extract_number("um cafe e um meio", lang="pt"), 1.5)
        self.assertEqual(extract_number("três quartos de chocolate", lang="pt"), 3.0 / 4.0)
        self.assertEqual(  # missing accent in "três"
            extract_number("tres quartos de chocolate", lang="pt"), 3.0 / 4.0)
        self.assertEqual(extract_number("três quarto de chocolate", lang="pt"), 3.0 / 4.0)
        self.assertEqual(extract_number("sete e meio", lang="pt"), 7.5)
        # for non english speakers,  "X Y avos" means X / Y
        self.assertEqual(extract_number("vinte treze avos", lang="pt"), 20.0 / 13.0)
        self.assertEqual(extract_number("um quinze avos", lang="pt"), 1.0 / 15.0)

        # N * fraction
        self.assertEqual(extract_number("dez vinte treze avos", lang="pt"),
                         10 * 20.0 / 13.0)

    def test_extract_decimal_numbers_pt(self):
        # number dot number
        self.assertEqual(extract_number("sete ponto cinco", lang="pt"), 7.5)
        self.assertEqual(extract_number("sete ponto 5", lang="pt"), 7.5)
        # TODO FIX ME, not parsing "e"

        # self.assertEqual(extract_number("seis virgula seiscentos e sessenta",
        #                                lang="pt"), 6.66)

        # TODO FIX ME, not taking 0 into account on number dot zero number number

        #  self.assertEqual(extract_number("seiscentos ponto zero seis",
        #                                        lang="pt"), 600.06)
        #  self.assertEqual(extract_number("seiscentos ponto zero zero seis",
        #                                        lang="pt"), 600.006)
        #   self.assertEqual(extract_number("seiscentos ponto zero zero zero seis",
        #                                        lang="pt"), 600.0006)

        # TODO get feedback from other native speakers
        # NOTE "e" used as a decimal marker is technically incorrect but
        # often used in everyday language, specially when talking about currency
        # decided to disable for now for correctness

        # self.assertEqual(extract_number("sete e oitenta", lang="pt"), 7.80)
        # ambiguous, most likely should be 7.08
        # self.assertEqual(extract_number("sete e oito", lang="pt"), 7.8)

        # to enable add "e" to common_data_pt._DECIMAL_MARKER_PT and disable tests bellow

        # NOTE: contains multiple numbers
        # extract_numbers should be used, only last number will be returned
        self.assertEqual(extract_number("sete e oitenta", lang="pt"), 80)
        self.assertEqual(extract_number("sete e oito", lang="pt"), 8)

    def test_extract_ordinal_numbers_pt(self):
        # equivalent to "1st", "2nd", .."nth"
        self.assertEqual(extract_number("isto e o 2º teste", lang="pt"), 2)
        self.assertEqual(extract_number("foi a 3º vez", lang="pt"), 3)
        # spoken ordinals
        self.assertEqual(extract_number("isto e o primeiro teste", lang="pt"), 1)
        self.assertEqual(extract_number("isto e o segundo teste", lang="pt"), 2)
        self.assertEqual(extract_number("isto e o terceiro teste", lang="pt"), 3)
        self.assertEqual(extract_number("isto e o quarto teste", lang="pt"), 1 / 4)
        # spoken ordinals sharing name with fractions
        self.assertEqual(extract_number("isto e o quarto teste", lang="pt", ordinals=True), 4)
        self.assertEqual(extract_number("isto e o milésimo teste", lang="pt", ordinals=True), 1000)

    def test_extract_negative_numbers_pt(self):
        self.assertEqual(extract_number("menos dois", lang="pt"), -2)
        self.assertEqual(extract_number("dois negativos", lang="pt"), -2)
        self.assertEqual(extract_number("dois graus negativos", lang="pt"), -2)
        self.assertEqual(extract_number("um grau negativo", lang="pt"), -1)
        # technically incorrect, makes use of double negative, but people say it
        self.assertEqual(extract_number("menos dois graus negativos", lang="pt"), -2)

    def test_extract_big_numbers_pt(self):
        # test sums, i.e,  "twenty two"
        self.assertEqual(extract_number("vinte dois", lang="pt"), 22)
        self.assertEqual(extract_number("mil cento trinta dois", lang="pt"), 1132)
        self.assertEqual(extract_number("vinte e dois", lang="pt"), 22)
        self.assertEqual(extract_number("seiscentos e sessenta e seis", lang="pt"), 666)
        self.assertEqual(extract_number("mil cento e trinta e dois", lang="pt"), 1132)
        self.assertEqual(extract_number("um milhão mil e trinta e dois", lang="pt"), 1001032)
        # test multplication, i.e,  "hundred thousand"
        self.assertEqual(extract_number("um milhão trezentos mil e trinta e dois", lang="pt"), 1300032)

    def test_extract_numbers_long_scale_pt(self):
        # portuguese is long_scale by default
        self.assertEqual(extract_number("um bilião", lang="pt"),
                         extract_number("um bilião", short_scale=False, lang="pt"))

        self.assertEqual(extract_number("um bilião", lang="pt"), 1e12)
        self.assertEqual(extract_number("um trilião", lang="pt"), 1e18)

    def test_extract_numbers_short_scale_pt(self):
        self.assertEqual(extract_number("um bilião", lang="pt", short_scale=False), 1e12)
        self.assertEqual(extract_number("um bilião", lang="pt", short_scale=True), 1e9)
        self.assertEqual(extract_number("um trilião", lang="pt", short_scale=True), 1e12)

    def test_agressive_pruning_pt(self):
        self.assertEqual(normalize("uma palavra", lang="pt"),
                         "1 palavra")
        self.assertEqual(normalize("esta palavra um", lang="pt"),
                         "palavra 1")
        self.assertEqual(normalize("o homem batia-lhe", lang="pt"),
                         "homem batia")
        self.assertEqual(normalize("quem disse asneira nesse dia", lang="pt"),
                         "quem disse asneira dia")

    def test_spaces_pt(self):
        self.assertEqual(normalize("  isto   e  o    teste", lang="pt"),
                         "isto teste")
        self.assertEqual(normalize("  isto   sao os    testes  ", lang="pt"),
                         "isto sao testes")
        self.assertEqual(normalize("  isto   e  um    teste", lang="pt", remove_articles=False),
                         "isto e 1 teste")

    def test_numbers_pt(self):
        self.assertEqual(normalize(u"isto e o um dois três teste", lang="pt"),
                         u"isto 1 2 3 teste")
        self.assertEqual(normalize(u"ê a sete oito nove  test", lang="pt"),
                         u"7 8 9 test")
        self.assertEqual(
            normalize("teste zero dez onze doze treze", lang="pt"),
            "teste 0 10 11 12 13")
        self.assertEqual(
            normalize("teste mil seiscentos e sessenta e seis", lang="pt",
                      remove_articles=False),
            "teste 1000 600 e 66")
        self.assertEqual(
            normalize("teste sete e meio", lang="pt",
                      remove_articles=False),
            "teste 7 e meio")
        self.assertEqual(
            normalize("teste dois ponto nove", lang="pt"),
            "teste 2 ponto 9")
        self.assertEqual(
            normalize("teste cento e nove", lang="pt",
                      remove_articles=False),
            "teste 100 e 9")
        self.assertEqual(
            normalize("teste vinte e 1", lang="pt"),
            "teste 20 1")

    def test_extractdatetime_pt(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 0, 0)
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang="pt")
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date)
            self.assertEqual(res[1], expected_leftover)

        testExtract(u"que dia é hoje",
                    "2017-06-27 00:00:00", u"dia")
        testExtract(u"que dia é amanha",
                    "2017-06-28 00:00:00", u"dia")
        testExtract(u"que dia foi ontem",
                    "2017-06-26 00:00:00", u"dia")
        testExtract(u"que dia foi antes de ontem",
                    "2017-06-25 00:00:00", u"dia")
        testExtract(u"que dia foi ante ontem",
                    "2017-06-25 00:00:00", u"dia")
        testExtract(u"que dia foi ante ante ontem",
                    "2017-06-24 00:00:00", u"dia")
        testExtract("marca o jantar em 5 dias",
                    "2017-07-02 00:00:00", "marca jantar")
        testExtract("como esta o tempo para o dia depois de amanha?",
                    "2017-06-29 00:00:00", "como tempo")
        testExtract(u"lembra me ás 10:45 pm",
                    "2017-06-27 22:45:00", u"lembra")
        testExtract("como esta o tempo na sexta de manha",
                    "2017-06-30 08:00:00", "como tempo")
        testExtract(u"lembra me para ligar a mãe daqui "
                    u"a 8 semanas e 2 dias",
                    "2017-08-24 00:00:00", u"lembra ligar mae")
        testExtract("Toca black metal 2 dias a seguir a sexta",
                    "2017-07-02 00:00:00", "toca black metal")
        testExtract("Toca satanic black metal 2 dias para esta sexta",
                    "2017-07-02 00:00:00", "toca satanic black metal")
        testExtract("Toca super black metal 2 dias a partir desta sexta",
                    "2017-07-02 00:00:00", "toca super black metal")
        testExtract(u"Começa a invasão ás 3:45 pm de quinta feira",
                    "2017-06-29 15:45:00", "comeca invasao")
        testExtract("na segunda, compra queijo",
                    "2017-07-03 00:00:00", "compra queijo")
        testExtract(u"Toca os parabéns daqui a 5 anos",
                    "2022-06-27 00:00:00", "toca parabens")
        testExtract(u"manda Skype a Mãe ás 12:45 pm próxima quinta",
                    "2017-06-29 12:45:00", "manda skype mae")
        testExtract(u"como está o tempo esta sexta?",
                    "2017-06-30 00:00:00", "como tempo")
        testExtract(u"como está o tempo esta sexta de tarde?",
                    "2017-06-30 15:00:00", "como tempo")
        testExtract(u"como está o tempo esta sexta as tantas da manha?",
                    "2017-06-30 04:00:00", "como tempo")
        testExtract(u"como está o tempo esta sexta a meia noite?",
                    "2017-06-30 00:00:00", "como tempo")
        testExtract(u"como está o tempo esta sexta ao meio dia?",
                    "2017-06-30 12:00:00", "como tempo")
        testExtract(u"como está o tempo esta sexta ao fim da tarde?",
                    "2017-06-30 19:00:00", "como tempo")
        testExtract(u"como está o tempo esta sexta ao meio da manha?",
                    "2017-06-30 10:00:00", "como tempo")
        testExtract("lembra me para ligar a mae no dia 3 de agosto",
                    "2017-08-03 00:00:00", "lembra ligar mae")

        testExtract(u"compra facas no 13º dia de maio",
                    "2018-05-13 00:00:00", "compra facas")
        testExtract(u"gasta dinheiro no maio dia 13",
                    "2018-05-13 00:00:00", "gasta dinheiro")
        testExtract(u"compra velas a maio 13",
                    "2018-05-13 00:00:00", "compra velas")
        testExtract(u"bebe cerveja a 13 maio",
                    "2018-05-13 00:00:00", "bebe cerveja")
        testExtract("como esta o tempo 1 dia a seguir a amanha",
                    "2017-06-29 00:00:00", "como tempo")
        testExtract(u"como esta o tempo ás 0700 horas",
                    "2017-06-27 07:00:00", "como tempo")
        testExtract(u"como esta o tempo amanha ás 7 em ponto",
                    "2017-06-28 07:00:00", "como tempo")
        testExtract(u"como esta o tempo amanha pelas 2 da tarde",
                    "2017-06-28 14:00:00", "como tempo")
        testExtract(u"como esta o tempo amanha pelas 2",
                    "2017-06-28 02:00:00", "como tempo")
        testExtract(u"como esta o tempo pelas 2 da tarde da proxima sexta",
                    "2017-06-30 14:00:00", "como tempo")
        testExtract("lembra-me de acordar em 4 anos",
                    "2021-06-27 00:00:00", "lembra acordar")
        testExtract("lembra-me de acordar em 4 anos e 4 dias",
                    "2021-07-01 00:00:00", "lembra acordar")
        testExtract("dorme 3 dias depois de amanha",
                    "2017-07-02 00:00:00", "dorme")
        testExtract("marca consulta para 2 semanas e 6 dias depois de Sabado",
                    "2017-07-21 00:00:00", "marca consulta")
        testExtract(u"começa a festa ás 8 em ponto da noite de quinta",
                    "2017-06-29 20:00:00", "comeca festa")

    def test_extractdatetime_default_pt(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime(
            'marca consulta para 2 semanas e 6 dias depois de Sabado',
            anchor, lang='pt-pt', default_time=default)
        self.assertEqual(default, res[0].time())

    def test_gender_pt(self):
        self.assertEqual(get_gender("vaca", lang="pt"), "f")
        self.assertEqual(get_gender("cavalo", lang="pt"), "m")
        self.assertEqual(get_gender("vacas", lang="pt"), "f")
        self.assertEqual(get_gender("boi", "o boi come erva", lang="pt"), "m")
        self.assertEqual(get_gender("boi", lang="pt"), None)
        self.assertEqual(get_gender("homem", "estes homem come merda",
                                    lang="pt"), "m")
        self.assertEqual(get_gender("ponte", lang="pt"), "m")
        self.assertEqual(get_gender("ponte", "essa ponte caiu",
                                    lang="pt"), "f")


if __name__ == "__main__":
    unittest.main()
