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
from datetime import datetime
import unittest

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.parse import (normalize, extract_numbers, extract_number,
                                 extract_datetime)
from lingua_franca.lang.parse_es import extract_datetime_gl-es, is_fractional_gl-es
from lingua_franca.time import default_timezone


def setUpModule():
    load_language('gl-es')
    set_default_lang('gl-es')


def tearDownModule():
    unload_language('gl-es')


class TestNormalize(unittest.TestCase):
    """
        Test cases for Galician parsing
    """

    def test_articles_gl-es(self):
        self.assertEqual(normalize("esta é a proba", lang="gl-es",
                                   remove_articles=True),
                         "esta es prueba")
        self.assertEqual(normalize("e outra proba", lang="gl-es",
                                   remove_articles=True),
                         "e outra proba")

    def test_numbers_gl-es(self):
        self.assertEqual(normalize("isto é un un un", lang="gl-es"),
                         "isto é 1 1 1")
        self.assertEqual(normalize("isto é dous tres proba", lang="gl-es"),
                         "isto é 2 3 proba")
        self.assertEqual(normalize("isto é catro cinco seis proba",
                                   lang="gl-es"),
                         "isto é 4 5 6 proba")
        self.assertEqual(normalize("sete mï¿½s oito mï¿½s nove", lang="gl-es"),
                         "7 mï¿½s 8 mï¿½s 9")
        self.assertEqual(normalize("dez once doce trece catorce quince",
                                   lang="gl-es"),
                         "10 11 12 13 14 15")
        self.assertEqual(normalize("dezaseis dezasete", lang="gl-es"),
                         "16 17")
        self.assertEqual(normalize("dezaoito dezanove", lang="gl-es"),
                         "18 19")
        self.assertEqual(normalize("vinte trinta corenta", lang="gl-es"),
                         "20 30 40")
        self.assertEqual(normalize("trinta e dous cabalos", lang="gl-es"),
                         "32 cabalos")
        self.assertEqual(normalize("cen cabalos", lang="gl-es"),
                         "100 cabalos")
        self.assertEqual(normalize("cento once cabalos", lang="gl-es"),
                         "111 cabalos")
        self.assertEqual(normalize("habï¿½a cuatrocentas unha vacas",
                                   lang="gl-es"),
                         "habï¿½a 401 vacas")
        self.assertEqual(normalize("dous mil", lang="gl-es"),
                         "2000")
        self.assertEqual(normalize("dous mil trescentas corenta e cinco",
                                   lang="gl-es"),
                         "2345")
        self.assertEqual(normalize(
            "cento vinte e tres mil catrocentas cincuenta e seis",
            lang="gl-es"),
            "123456")
        self.assertEqual(normalize(
            "cincocentas vinte e cinco mil", lang="gl-es"),
            "525000")
        self.assertEqual(normalize(
            "novecentos noventa e nove mil novecentos noventa e nove",
            lang="gl-es"),
            "999999")

    def test_extract_number_es(self):
        self.assertEqual(sorted(extract_numbers(
            "1 7 catro catorce oito 157", lang='gl-es')), [1, 4, 7, 8, 14, 157])
        self.assertEqual(sorted(extract_numbers(
            "1 7 catro albuquerque laranxa John Doe catorce oito 157",
            lang='gl-es')), [1, 4, 7, 8, 14, 157])
        self.assertEqual(extract_number("seis punto dous", lang='gl-es'), 6.2)
        self.assertEqual(extract_number("seis punto dous", lang='gl-es'), 6.2)
        self.assertEqual(extract_number("seis coma dous", lang='gl-es'), 6.2)
        self.assertEqual(extract_numbers("un medio", lang='gl-es'), [0.5])
        self.assertEqual(extract_number("cuarto", lang='gl-es'), 0.25)

        self.assertEqual(extract_number("2.0", lang='gl-es'), 2.0)
        self.assertEqual(extract_number("1/4", lang='gl-es'), 0.25)

        self.assertEqual(extract_number("dous e media", lang='gl-es'), 2.5)
        self.assertEqual(extract_number(
            "catorce e milésima", lang='gl-es'), 14.001)

        self.assertEqual(extract_number("dous punto cero dous", lang='gl-es'), 2.02)

    def test_isFraction_es(self):
        self.assertEqual(is_fractional_gl-es("vixésimo"), 1.0 / 20)
        self.assertEqual(is_fractional_gl-es("vixésima"), 1.0 / 20)
        self.assertEqual(is_fractional_gl-es("trixésimo"), 1.0 / 30)
        self.assertEqual(is_fractional_gl-es("centésima"), 1.0 / 100)
        self.assertEqual(is_fractional_gl-es("centésimo"), 1.0 / 100)
        self.assertEqual(is_fractional_gl-es("milésima"), 1.0 / 1000)

    @unittest.skip("unwritten logic")
    def test_comma_fraction_logic_gl-es(self):
        # Logic has not been written to parse "#,#" as "#.#"
        # English-style decimal numbers work because they just get float(str)ed
        self.assertEqual(extract_number("2,0", lang='gl-es'), 2.0)


class TestDatetime_gl-es(unittest.TestCase):

    def test_datetime_by_date_gl-es(self):
        # test currentDate==None
        _now = datetime.now()
        relative_year = _now.year if (_now.month == 1 and _now.day < 11) else \
            (_now.year + 1)
        self.assertEqual(extract_datetime_gl-es("11 ene", anchorDate=_now)[0],
                         datetime(relative_year, 1, 11))

        # test months
        self.assertEqual(extract_datetime(
            "11 xan", lang='gl-es', anchorDate=datetime(1998, 1, 1))[0],
            datetime(1998, 1, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 feb", lang='gl-es', anchorDate=datetime(1998, 2, 1))[0],
            datetime(1998, 2, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mar", lang='gl-es', anchorDate=datetime(1998, 3, 1))[0],
            datetime(1998, 3, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 abr", lang='gl-es', anchorDate=datetime(1998, 4, 1))[0],
            datetime(1998, 4, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 mai", lang='gl-es', anchorDate=datetime(1998, 5, 1))[0],
            datetime(1998, 5, 11, tzinfo=default_timezone()))
        # there is an issue with the months of june through september (below)
        # hai un problema cos meses desde xuño ata setembro (lea abaixo)
        self.assertEqual(extract_datetime(
            "11 out", lang='gl-es', anchorDate=datetime(1998, 10, 1))[0],
            datetime(1998, 10, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 nov", lang='gl-es', anchorDate=datetime(1998, 11, 1))[0],
            datetime(1998, 11, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 dec", lang='gl-es', anchorDate=datetime(1998, 12, 1))[0],
            datetime(1998, 12, 11, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("", lang='gl-es'), None)

    # TODO fix bug causing these tests to fail (MycroftAI/mycroft-core#2348)
    #         reparar erro de tradución previndo as funcións abaixo de
    #         retornar correctamente
    #         (escrito con desculpas por un Inglés hablante)
    #      further broken tests are below their respective working tests.
    @unittest.skip("currently processing these months incorrectly")
    def test_bugged_output_wastebasket(self):
        self.assertEqual(extract_datetime(
            "11 xuñ", lang='gl-es', anchorDate=datetime(1998, 6, 1))[0],
            datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 xuño", lang='gl-es', anchorDate=datetime(1998, 6, 1))[0],
            datetime(1998, 6, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 xul", lang='gl-es', anchorDate=datetime(1998, 7, 1))[0],
            datetime(1998, 7, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 ago", lang='gl-es', anchorDate=datetime(1998, 8, 1))[0],
            datetime(1998, 8, 11, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "11 set", lang='gl-es', anchorDate=datetime(1998, 9, 1))[0],
            datetime(1998, 9, 11, tzinfo=default_timezone()))

        # It's also failing on years
        self.assertEqual(extract_datetime(
            "11 ago 1998", lang='gl-es')[0],
                         datetime(1998, 8, 11, tzinfo=default_timezone()))

    def test_extract_datetime_relative(self):
        self.assertEqual(extract_datetime(
            "esta noite", anchorDate=datetime(1998, 1, 1),
            lang='gl-es'), [datetime(1998, 1, 1, 21, 0, 0, tzinfo=default_timezone()), 'esta'])
        self.assertEqual(extract_datetime(
            "onte á noite", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 31, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "a noite de antonte", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 30, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "a noite de antes de antonte", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 29, 21, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "mañá pola mañá", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1998, 1, 2, 8, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime(
            "onte pola tarde", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 31, 15, tzinfo=default_timezone()))

        self.assertEqual(extract_datetime("hoxe ás 2 da mañá", lang='gl-es',
                                          anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 2, tzinfo=default_timezone()))
        self.assertEqual(extract_datetime("hoxe ás 2 da tarde", lang='gl-es',
                                          anchorDate=datetime(1998, 1, 1))[0],
                         datetime(1998, 1, 1, 14, tzinfo=default_timezone()))

    def test_extractdatetime_no_time(self):
        """Check that None is returned if no time is found in sentence."""
        self.assertEqual(extract_datetime('non hai tempo', lang='gl-es'), None)

    @unittest.skip("These phrases are not parsing correctly.")
    def test_extract_datetime_relative_failing(self):
        # parses as "morning" and returns 8:00 on anchorDate
        self.assertEqual(extract_datetime(
            "mañá", anchorDate=datetime(1998, 1, 1), lang='gl-es')[0],
            datetime(1998, 1, 2))

        # unimplemented logic
        self.assertEqual(extract_datetime(
            "onte á noite", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 31, 21))
        self.assertEqual(extract_datetime(
            "antonte á noite", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 30, 21))
        self.assertEqual(extract_datetime(
            "fai tres noites", anchorDate=datetime(1998, 1, 1),
            lang='gl-es')[0], datetime(1997, 12, 29, 21))


if __name__ == "__main__":
    unittest.main()
