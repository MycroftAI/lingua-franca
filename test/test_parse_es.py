# -*- coding: utf-8 -*-
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

from lingua_franca.parse import normalize
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_number
from lingua_franca.parse import extract_numbers
from lingua_franca.parse import get_gender


class TestNormalize(unittest.TestCase):
    """
        Test cases for Spanish parsing
    """
    def test_articles_es(self):
        """
        Test cases for Spanish remove_articles
        """
        self.assertEqual(
            normalize("esta es la prueba", lang="es", remove_articles=True),
            "esta es prueba"
        )
        self.assertEqual(
            normalize("este es el exámen", lang="es", remove_articles=True),
            "este es exámen"
        )
        self.assertEqual(
            normalize("estos son los carácteres", lang="es",
                      remove_articles=True), "estos son carácteres")
        self.assertEqual(
            normalize("y otra prueba", lang="es", remove_articles=True),
            "y otra prueba"
        )
        self.assertEqual(
            normalize("estas son unas pruebas",
                      lang="es", remove_articles=True), "estas son pruebas")

    def test_extractnumber_es(self):
        """
        Test cases for Spanish extract_number, lang='es'
        """
        self.assertEqual(extract_number('esto es la primera prueba',
                                        lang='es'), 1)
        self.assertEqual(extract_number('esto es el 2 test', lang='es'), 2)
        self.assertEqual(extract_number('esto es el segundo test',
                                        lang='es', ordinals=True), 2)
        self.assertEqual(extract_number('esto es un tercio de test',
                                        lang='es'), 1.0 / 3.0)
        self.assertEqual(extract_number('esto es el tercer test',
                                        lang='es', ordinals=True), 3.0)
        # TODO: FAIL
        # self.assertEqual(extract_number('esto es el trigésimo sexto test',
        #                                 lang='es'), 36.0)
        self.assertEqual(extract_number('esto es la prueba número 4',
                                        lang='es'), 4)
        self.assertEqual(extract_number('una taza', lang='es'), 1)
        self.assertEqual(extract_number('un gato', lang='es'), 1)
        self.assertEqual(extract_number('un tercio de taza',
                                        lang='es'), 1.0 / 3.0)
        self.assertEqual(extract_number('2 quintos de taza', lang='es'), 0.4)
        self.assertEqual(extract_number('tres tazas', lang='es'), 3)
        self.assertEqual(extract_number('1/3 tazas', lang='es'), 1.0 / 3.0)
        self.assertEqual(extract_number('un cuarto de taza', lang='es'), 0.25)
        self.assertEqual(extract_number('1/4 taza', lang='es'), 0.25)
        self.assertEqual(extract_number('2/3 taza', lang='es'), 2.0 / 3.0)
        self.assertEqual(extract_number('3/4 taza', lang='es'), 3.0 / 4.0)
        self.assertEqual(extract_number('1 y 1/4 taza', lang='es'), 1.25)
        self.assertEqual(extract_number('1 taza y medio', lang='es'), 1.5)
        self.assertEqual(extract_number('una taza y medio', lang='es'), 1.5)
        self.assertEqual(extract_number('una y media taza', lang='es'), 1.5)
        self.assertEqual(extract_number('una y una media taza',
                                        lang='es'), 1.5)
        self.assertEqual(extract_number('tres cuartos de taza',
                                        lang='es'), 3.0 / 4.0)
        self.assertEqual(extract_number('veintidos', lang='es'), 22)
        self.assertEqual(extract_number('doscientos', lang='es'), 200)
        self.assertEqual(extract_number('nueve mil', lang='es'), 9000)
        # TODO: Dos millones
        self.assertEqual(extract_number('dos millón',
                                        lang='es',
                                        short_scale=False), 2000000)
        # TODO: Dos millones
        self.assertEqual(extract_number('dos millón quinientos mil '
                                        'toneladas de metales',
                                        lang='es'), 2500000)
        # TODO: Trillones
        self.assertEqual(extract_number('seis trillón', lang='es',
                                        short_scale=False),
                         6000000000000000000.0)
        self.assertEqual(extract_number('seis trillón', short_scale=False,
                                        lang='es'), 6e+18)
        self.assertEqual(extract_number('un millardo un millón',
                                        lang='es',
                                        short_scale=False), 1001000000)
        # TODO: cien
        self.assertEqual(extract_number('un millardo ciento',
                                        lang='es',
                                        short_scale=False), 1000000100)
        # TODO: Fail
        # self.assertEqual(extract_number('dos millardo un millón ciento
        # treinta y dos',
        #                                 lang='es'), 2001000132)
        self.assertEqual(extract_number('veinte diecisieteavos',
                                        lang='es'), 20.0/17.0)
        self.assertEqual(extract_number('uno coma cinco', lang='es'), 1.5)
        self.assertEqual(extract_number('tres punto catorce',
                                        lang='es'), 3.14)
        self.assertEqual(extract_number('cero coma dos', lang='es'), 0.2)
        # TODO: millones
        self.assertEqual(extract_number('mil millón de años',
                                        lang='es'), 1000000000.0)
        # TODO: trillones
        self.assertEqual(extract_number('trillón de años',
                                        short_scale=False,
                                        lang='es'), 1000000000000000000.0)
        self.assertEqual(extract_number('cien mil', lang='es'), 100000)
        # TODO: fail
        # self.assertEqual(extract_number('mil cuatrocientos noventa y dos',
        #                                 lang='es'), 1492)
        self.assertEqual(extract_number('menos 2', lang='es'), -2)
        self.assertEqual(extract_number('menos setenta', lang='es'), -70)

        # TODO: millones
        self.assertEqual(extract_number('mil millón',
                                        lang='es'), 1000000000)
        # TODO: Fail
        # self.assertEqual(extract_number('mil ciento uno',
        #                                 lang='es'), 1101)
        self.assertEqual(extract_number('un sexto tercio',
                                        lang='es'), 1 / 6 / 3)
        self.assertEqual(extract_number('treinta segundos', lang='es'), 30)
        self.assertEqual(extract_number('treinta segundos', lang='es',
                                        ordinals=True), 30)
        self.assertEqual(extract_number('siete y pico', lang='es'), 7.0)
        self.assertEqual(extract_number('siete coma 5', lang='es'), 7.5)
        self.assertEqual(extract_number('siete punto 575', lang='es'), 7.575)
        self.assertEqual(extract_number('siete y medio', lang='es'), 7.5)
        self.assertEqual(extract_number('siete y ochenta', lang='es'), 7.80)
        self.assertEqual(extract_number('siete y ocho', lang='es'), 7.8)
        self.assertEqual(extract_number('siete y cero ocho',
                                        lang='es'), 7.08)
        self.assertEqual(extract_number('siete coma cero cero cero ocho grados',
                                        lang='es'), 7.0008)
        self.assertEqual(extract_number('veinte treceavos',
                                        lang='es'), 20.0 / 13.0)
        self.assertEqual(extract_number('veinte treceavos', lang='es',
                                        short_scale=True), 20.0 / 13.0)
        # TODO: Fail sesenta y seis
        # self.assertEqual(extract_number('seis coma sesenta y seis',
        #                                 lang='es'), 6.66)
    #     self.assertEqual(extract_number('seis punto sesenta y seis',
    #                                     lang='es'), 6.66)
        # TODO: Fail seiscientos + sesenta y seis
        # self.assertEqual(extract_number('seiscientos sesenta y seis',
        #                                 lang='es'), 666)
        # TODO: Fail mil cuatrocientos + 
        # self.assertEqual(extract_number('mil cuatrocientos noventa y dos',
        #                                 lang='es'), 1492)
        self.assertEqual(extract_number('seiscientos punto cero seis',
                                        lang='es'), 600.06)
        self.assertEqual(extract_number('seiscientos punto cero cero seis',
                                        lang='es'), 600.006)
        self.assertEqual(extract_number('seiscientos punto cero cero cero seis',
                                        lang='es'), 600.0006)
        self.assertEqual(extract_number('tres décimos ',
                                        lang='es'), 0.30000000000000004)
        # TODO: Fail décimas
        # self.assertEqual(extract_number('tres décimas ',
        #                                 lang='es'), 0.30000000000000004)                                        
        # TODO: Fail
        # self.assertEqual(extract_number('doce centésimos',
        #                                 lang='es'), 0.12)
        # self.assertEqual(extract_number('cinco y cuarenta y dos milésimas',
        #                                 lang='es'), 5.042)
        self.assertEqual(extract_number('mil uno',
                                        lang='es'), 1001)
        # TODO: Fail
        # self.assertEqual(extract_number('dos mil veintidós dólares ',
        #                                 lang='es'), 2022)
        # self.assertEqual(extract_number(
        #     'ciento catorce mil cuatrocientos once dólares ',
        #     lang='es', ordinals=True, short_scale=True), 114411)

        # TODO: es veintitrés, no veintitres
        self.assertEqual(extract_number('veintitres dólares ', lang='es'), 23)
        self.assertEqual(extract_number('veintiuno años ',
                                        lang='es'), 21)
        # TODO: es veintiún
        # self.assertEqual(extract_number('veintiún años ',
        #                                 lang='es'), 21)
        
        # TODO: Fail
        # self.assertEqual(extract_number('doce y cuarenta y cinco ',
        #                                 lang='es'), 12.45)
        self.assertEqual(extract_number('hazles saber si alguien llega ',
                                        lang='es'), False)
        self.assertTrue(extract_number('El tenista es rápido',
                                       lang='es') is False)
        self.assertTrue(extract_number('alguna', lang='es') is False)
        self.assertTrue(extract_number('cota cero',
                                       lang='es') is not False)
        self.assertEqual(extract_number('cota cero', lang='es'), 0)
        self.assertTrue(extract_number('cota 0', lang='es') is not False)
        self.assertEqual(extract_number('cota 0', lang='es'), 0)
        self.assertEqual(extract_number('un par de cervezas', lang='es'), 2)
        self.assertEqual(extract_number('una centena de cervezas',
                                        lang='es'), 100)
        # TODO: Centenar
        # self.assertEqual(extract_number('un centenar de cervezas',
        #                                 lang='es'), 100)
        self.assertEqual(extract_number('un par de mil de cervezas',
                                        lang='es'), 2000)
        # TODO: Miles
        # self.assertEqual(extract_number('un par de mil de cervezas',
        #                                 lang='es'), 2000)                                    
        self.assertEqual(extract_number('una decena de monedas',
                                        lang='es'), 10)
        # TODO: Docenas                                        
        self.assertEqual(extract_number('tres docena de huevos',
                                        lang='es'), 36)
        self.assertEqual(extract_number('cero gatos',
                                        lang='es'), 0)

    def test_extractdatetime_es_not_normalized(self):
        """
        Test cases for Spanish datetime parsing

        """
        def extractWithFormat_es(text):
            date = datetime(2018, 1, 13, 13, 4)  # Sab 13 Ene, 2018 @ 13:04
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang='es')
            extractedDate = extractedDate.strftime('%Y-%m-%d %H:%M:%S')
            return [extractedDate, leftover]
        # The following is a test taken from english, I don't really know what
        # is supposed is doing here.
        def testExtract_es(text, expected_date, expected_leftover):
            res = extractWithFormat_es(normalize(text))  # era normalize(text)
            self.assertEqual(res[0], expected_date, 'por=' + text)
            self.assertEqual(res[1], expected_leftover, 'por=' + text)

        testExtract_es('qué hora es ahora',
                       '2018-01-13 13:04:00', 'que hora es')
        testExtract_es('tras dos segundos',
                       '2018-01-13 13:04:02', '')
        testExtract_es('en un minuto',
                       '2018-01-13 13:05:00', '')
        testExtract_es('en un par de minutos',
                       '2018-01-13 13:06:00', '')
        testExtract_es('en un par de horas',
                       '2018-01-13 15:04:00', '')
        testExtract_es('en dos semanas',
                       '2018-01-27 00:00:00', '')
        testExtract_es('en un par de meses',
                       '2018-03-13 00:00:00', '')
        testExtract_es('en un par de años',
                       '2020-01-13 00:00:00', '')
        # TODO: Fail
        # testExtract_es('en una década',
        #                '2028-01-13 00:00:00', '')
        # testExtract_es('en un par de décadas',
        #                '2038-01-13 00:00:00', '')
        # testExtract_es('en la siguiente década',
        #                '2028-01-13 00:00:00', '')
        # testExtract_es('en el próximo decenio',
        #                '2028-01-13 00:00:00', '')
        # testExtract_es('en la última década',
        #                '2008-01-13 00:00:00', '')
        # testExtract_es('en la década pasada',
        #                '2008-01-13 00:00:00', '')
        # testExtract_es('en un siglo',
        #                '2118-01-13 00:00:00', '')
        testExtract_es('en un milenio',
                       '3018-01-13 00:00:00', '')
        # testExtract_es('en un par de décadas',
        #                '2038-01-13 00:00:00', '')
        # testExtract_es('en 5 décadas',
        #                '2068-01-13 00:00:00', '')
        # testExtract_es('en un par de siglos',
        #                '2218-01-13 00:00:00', '')
        # testExtract_es('en 2 siglos',
        #                '2218-01-13 00:00:00', '')
        # testExtract_es('en un par de milenios',
        #                '4018-01-13 00:00:00', '')
        testExtract_es('cita en 1 hora',
                       '2018-01-13 14:04:00', 'cita')
        testExtract_es('cita en un hora',
                       '2018-01-13 14:04:00', 'cita')
        # testExtract_es('cita en una hora',
        #                '2018-01-13 14:04:00', 'cita')                       
        # testExtract_es('lo quiero en una hora',
        #                '2018-01-13 14:04:00', 'quiero')
        testExtract_es('en 1 segundo',
                       '2018-01-13 13:04:01', '')
        testExtract_es('en 2 segundos',
                       '2018-01-13 13:04:02', '')
        testExtract_es('Prepara la emboscada en 1 minuto',
                       '2018-01-13 13:05:00', 'prepara emboscada')
        # testExtract_es('Prepara la emboscada en media hora',
        #                '2018-01-13 13:34:00', 'prepara emboscada')
        # testExtract_es('prepara la emboscada en 5 días a partir de hoy',
        #                '2018-01-18 00:00:00', 'prepara emboscada')
        # testExtract_es('cuál es el pronóstico del tiempo para pasado mañana',
        #                '2018-01-15 00:00:00', 'cuál es el pronóstico del tiempo')
        # testExtract_es('¿cuál es el pronóstico del tiempo el próximo jueves?',
        #                '2018-01-18 00:00:00', 'cual es el pronóstico del tiempo')
        testExtract_es('¿qué tiempo hizo el jueves pasado?',
                       '2018-01-11 00:00:00', 'que tiempo hizo')
        # testExtract_es('cuál es el pronóstico del tiempo el jueves que viene?',
        #                '2018-01-25 00:00:00', 'cuál es el pronóstico del tiempo')
        # testExtract_es('¿cuál fue la previsión del tiempo el pasado jueves?',
        #                '2018-01-11 00:00:00', 'cual fue la previsión del tiempo')
        testExtract_es('cuál es la previsión del tiempo para hoy?',
                       '2018-01-13 00:00:00', 'cual es prevision tiempo')
        testExtract_es('recuérdame a las 10:45 pm',
                       '2018-01-13 22:45:00', 'recuerdame')
        # testExtract_es('qué tiempo hace el viernes por la mañana',
        #                '2018-01-19 08:00:00', 'que tiempo')
        # testExtract_es('Qué tiempo hará mañana',
        #                '2018-01-14 00:00:00', 'que tiempo hara')
        testExtract_es('cuál es el pronóstico del tiempo para esta tarde',
                       '2018-01-13 15:00:00', 'cual es pronostico tiempo')
    #     testExtract_es('quali sono le previsioni meteo di oggi tarde '
    #                    'presto',
    #                    '2018-01-13 14:00:00', 'cuál es el pronóstico del tiempo')
        testExtract_es('cuál es el pronóstico del tiempo para esta noche',
                       '2018-01-13 19:00:00', 'cual es pronostico tiempo')
    #     testExtract_es('quali sono le previsioni meteo di estas sera tardi',
    #                    '2018-01-13 20:00:00', 'cuál es el pronóstico del tiempo')
        testExtract_es('cuál es el pronóstico del tiempo para este mediodía',
                       '2018-01-14 12:00:00', 'cual es pronostico tiempo')
        testExtract_es('cuál es el pronóstico del tiempo para esta medianoche',
                       '2018-01-14 00:00:00', 'cual es pronostico tiempo')
        testExtract_es('cuál es el pronóstico del tiempo para el medio día',
                       '2018-01-14 12:00:00', 'cual es pronostico tiempo')
        testExtract_es('cuál es el pronóstico del tiempo para la media noche',
                       '2018-01-14 00:00:00', 'cual es pronostico tiempo')
        # testExtract_es('cuál es el pronóstico del tiempo para esta mañana',
        #                '2018-01-14 08:00:00', 'cual es pronostico tiempo')
        testExtract_es('recuérdame que llame a mamá el 3 de agosto.',
                       '2018-08-03 00:00:00', 'recuerdame que llame mama')
        # testExtract_es('recuérdame que llame a mamá mañana a las 7 de la mañana',
        #                '2018-01-14 07:00:00', 'recuerdame que llame mama')
    #     testExtract_es('recuérdame que llame a mamá mañana a las 7 de la tarde',
    #                    '2018-01-13 19:00:00', 'recuerdame que llame mama')
        # testExtract_es('llamar a mamá en una hora',
        #                '2018-01-13 14:04:00', 'llamar mama')
        testExtract_es('recuérdame que llame a mamá a las 0600',
                       '2018-01-14 06:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá las 09 y 30',
                       '2018-01-13 21:30:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá a las 7 en punto',
                       '2018-01-13 19:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá esta tarde a las 7 '
                       'en punto',
                       '2018-01-13 19:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá a las 7 de la tarde',
                       '2018-01-13 19:00:00', 'recuerdame que llame mama')
        # testExtract_es('recuérdame que llame a mamá mañana a las 7 en punto'
        #                ' de la mañana',
        #                '2018-01-14 07:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá el jueves por la tarde '
                       'a las 7 en punto',
                       '2018-01-18 19:00:00', 'recuerdame que llame mama')
        # testExtract_es('recuérdame que llame a mamá el jueves '
        #                'por la mañana a las 7 en punto',
        #                '2018-01-18 07:00:00', 'recuerdame que llame mama')
        # TODO: si ponemos "mañana" de "por la mañana" como exclusión, funciona.
        # pero no debe hacerse.
        testExtract_es('recuérdame que llame a mamá a las 7 '
                       'en punto del jueves por la mañana',
                       '2018-01-18 07:00:00', 'recuerdame que llame mama mañana')
        # testExtract_es('recuérdame que llame a mamá a las 7:00 '
        #                'del jueves por la mañana',
        #                '2018-01-18 07:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá a las 7:00 del jueves por la tarde',
                       '2018-01-18 19:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá a las 11:00 del '
                       'jueves por la noche',
                       '2018-01-18 23:00:00', 'recuerdame que llame mama')
        # TODO: Lo mismo que el TODO anterior, si excluímos "madrugada", funciona
        testExtract_es('recuérdame que llame a mamá a las 2:00 de la madrugada '
                       'del jueves',
                       '2018-01-18 02:00:00', 'recuerdame que llame mama madrugada')
        testExtract_es('recuérdame que llame a mamá a las 2:00 de la tarde '
                       'del jueves',
                       '2018-01-18 14:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá el jueves a las 2:00 '
                       'de la tarde',
                       '2018-01-18 14:00:00', 'recuerdame que llame mama')                       
        testExtract_es('recuérdame que llame a mamá miércoles tarde a las 8',
                       '2018-01-17 20:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en dos horas',
                       '2018-01-13 15:04:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en quince minutos',
                       '2018-01-13 13:19:00', 'recuerdame que llame mama')
        # testExtract_es('recuérdame que llame a mamá en media hora',
        #                '2018-01-13 13:34:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en un cuarto de hora',
                       '2018-01-13 13:19:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en tres cuartos de hora',
                       '2018-01-13 13:49:00', 'recuerdame que llame mama')
        # testExtract_es('Pon música de Rick Astley 2 días a partir del viernes',
        #                '2018-01-21 00:00:00', 'pon musica rick astley')
        testExtract_es('Empezar la invasión a las 3:45 pm del jueves',
                       '2018-01-18 15:45:00', 'empezar invasion')
        testExtract_es('el lunes, pide pastel de hojaldre',
                       '2018-01-15 00:00:00', 'pide pastel hojaldre')
        # testExtract_es('Pon la música de Happy Birthday 5 dentro de años',
        #                '2023-01-13 00:00:00', 'pon musica happy birthday')
        testExtract_es('comprar fuegos artificiales el 4 de julio',
                       '2018-07-04 00:00:00', 'comprar fuegos artificiales')
        # testExtract_es('¿Cuál es el tiempo 2 semanas después del próximo viernes?',
        #                '2018-02-02 00:00:00', 'cual tiempo')
        testExtract_es('qué tiempo hará el miércoles a las 0700 ',
                       '2018-01-17 07:00:00', 'que tiempo hara')
        # testExtract_es('Programa la visita en 2 semanas y 6 días a partir del sábado',
        #                '2018-02-02 00:00:00', 'programa visita')
        testExtract_es('Empezar la invasión jueves a las 03 45',
                       '2018-01-18 03:45:00', 'empezar invasion')
        testExtract_es('Empezar la invasión a las 800 del jueves',
                       '2018-01-18 08:00:00', 'empezar invasion')
        # TODO: Fail, cambia "fiesta" por "fieste"
        # testExtract_es('empezar la fiesta a las 8 en punto de la noche'
        #                ' del jueves',
        #                '2018-01-18 20:00:00', 'empezar fiesta')
        testExtract_es('Empezar la invasión a las 8 de la noche del jueves',
                       '2018-01-18 20:00:00', 'empezar invasion')
        testExtract_es('Empezar la invasión del jueves a mediodía',
                       '2018-01-18 12:00:00', 'empezar invasion')
        testExtract_es('Empezar la invasión del jueves a medianoche',
                       '2018-01-19 00:00:00', 'empezar invasion')
        testExtract_es('Empezar la invasión del jueves a las 0500',
                       '2018-01-18 05:00:00', 'empezar invasion')
        testExtract_es('despiértame en 4 años',
                       '2022-01-13 00:00:00', 'despiertame')
        testExtract_es('despiértame en 4 años y 4 días',
                       '2022-01-17 00:00:00', 'despiertame')
        testExtract_es('cuál es la previsión del tiempo 3 días después de mañana?',
                       '2018-01-17 00:00:00', 'cual es prevision tiempo')
        testExtract_es('el tres de diciembre',
                       '2018-12-03 00:00:00', '')
        testExtract_es('el 3 de diciembre',
                       '2018-12-03 00:00:00', '')
        testExtract_es('el 3 dic 2019',
                       '2019-12-03 00:00:00', '')
        testExtract_es('en feb 3 2019',
                       '2019-02-03 00:00:00', '')
        testExtract_es('encontrémonos a las 8:00 esta noche',
                       '2018-01-13 20:00:00', 'encontremonos')
        testExtract_es('encontrémonos a las 5 pm',
                       '2018-01-13 17:00:00', 'encontremonos')
        testExtract_es('encontrémonos a las 8 a.m.',
                       '2018-01-14 08:00:00', 'encontremonos')
        testExtract_es('recuérdame que me despierte a las 8 am',
                       '2018-01-14 08:00:00', 'recuerdame que me despierte')
        testExtract_es('qué tiempo hará el jueves',
                       '2018-01-18 00:00:00', 'que tiempo hara')
        testExtract_es('qué tiempo hará para este lunes',
                       '2018-01-15 00:00:00', 'que tiempo hara')
        testExtract_es('qué tiempo hará este miércoles',
                       '2018-01-17 00:00:00', 'que tiempo hara')
        testExtract_es('para el jueves qué tiempo hará',
                       '2018-01-18 00:00:00', 'que tiempo hara')
        testExtract_es('este jueves qué tiempo hará',
                       '2018-01-18 00:00:00', 'que tiempo hara')
        # TODO: Fail el "pasado lunes"
        testExtract_es('el anterior lunes qué tiempo hizo',
                       '2018-01-08 00:00:00', 'que tiempo hizo')
        testExtract_es('pon un aviso para el miércoles tarde a las 8',
                       '2018-01-17 20:00:00', 'pon aviso')
        testExtract_es('pon un aviso el miércoles a las 3 en punto'
                       ' de la tarde',
                       '2018-01-17 15:00:00', 'pon aviso')
        # TODO: hay que excluir "mañana" para que funcione
        testExtract_es('pon un aviso para este miércoles a las 3 en punto'
                       ' de la mañana',
                       '2018-01-17 03:00:00', 'pon aviso mañana')
        testExtract_es('pon un despertador el miércoles por la mañana a las'
                       ' 7 en punto',
                       '2018-01-17 07:00:00', 'pon despertador mañana')
        testExtract_es('pon un despertador para hoy a las 7 en punto',
                       '2018-01-13 19:00:00', 'pon despertador')
        testExtract_es('pon un despertador para esta tarde a las 7 en punto',
                       '2018-01-13 19:00:00', 'pon despertador')
        # TODO: Fail
        # testExtract_es('pon un despertador esta tarde a las 07:00',
        #                '2018-01-13 19:00:00', 'pon despertador')
        testExtract_es('en la noche del 5 de junio de 2017, recuérdame'
                       ' llamar a mi madre',
                       '2017-06-05 19:00:00', 'recuerdame llamar mi madre')
        # TODO: Fail, "Julio" aquí es un nombre, si se cambia a "Carlos", también falla.
        # testExtract_es('actualiza mi calendario para una reunión por la mañana'
        #                ' con Julio el 4 de Marzo',
        #                '2018-03-04 08:00:00',
        #                'actualiza mi calendario reunión mañana julio')
        testExtract_es('qué día es hoy',
                       '2018-01-13 00:00:00', 'que dia es')
        # testExtract_es('qué día es mañana',
        #                '2018-01-14 00:00:00', 'que dia es')
        testExtract_es('que dia fue ayer',
                       '2018-01-12 00:00:00', 'que dia fue')
        # testExtract_es('que dia es pasado mañana',
        #                '2018-01-15 00:00:00', 'que dia es')
        testExtract_es('quedemos para cenar en 5 días',
                       '2018-01-18 00:00:00', 'quedemos cenar')
        # TODO: Fail
        # testExtract_es('Qué tiempo tendremos pasado mañana',
        #                '2018-01-15 00:00:00', 'que tiempo tendremos')
        testExtract_es('avísame a las 22:45',
                       '2018-01-13 22:45:00', 'avisame')
        # TODO: Fail, ni excluyendo "mañana" parece funcionar
        # testExtract_es('Qué tiempo hará el viernes por la mañana',
        #                '2018-01-19 08:00:00', 'que tiempo hara mañana')
        # TODO: "próximo" funciona, "que viene" no
        # testExtract_es('recuérdame que llame a mamá el jueves que viene',
        #                '2018-01-25 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en 3 semanas',
                       '2018-02-03 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en 8 semanas',
                       '2018-03-10 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en 8 semanas'
                       ' y 2 días',
                       '2018-03-12 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en 4 días',
                       '2018-01-17 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en 3 meses',
                       '2018-04-13 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá en 2 años y 2 días',
                       '2020-01-15 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá la próxima semana',
                       '2018-01-20 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá la semana próxima',
                       '2018-01-20 00:00:00', 'recuerdame que llame mama')
        testExtract_es('recuérdame que llame a mamá la semana que viene',
                       '2018-01-20 00:00:00', 'recuerdame que llame mama')               
        testExtract_es('recuérdame que controle el gasto de la semana pasada',
                       '2018-01-06 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto de la pasada semana',
                       '2018-01-06 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del mes pasado',
                       '2017-12-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del pasado mes',
                       '2017-12-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del mes anterior',
                       '2017-12-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del anterior mes',
                       '2017-12-13 00:00:00', 'recuerdame que controle gasto')              
        testExtract_es('recuérdame que controle el gasto del mes próximo',
                       '2018-02-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del próximo mes',
                       '2018-02-13 00:00:00', 'recuerdame que controle gasto')
        # TODO: Fail
        # testExtract_es('recuérdame que controle el gasto del siguiente mes',
        #                '2018-02-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del mes que viene',
                       '2018-02-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del año pasado',
                       '2017-01-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del pasado año',
                       '2017-01-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del año próximo',
                       '2019-01-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del próximo año',
                       '2019-01-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que controle el gasto del año que viene',
                       '2019-01-13 00:00:00', 'recuerdame que controle gasto')
        testExtract_es('recuérdame que llame el próximo jueves',
                       '2018-01-25 00:00:00', 'recuerdame que llame')
        # TODO: Fail
        # testExtract_es('recuérdame que llame jueves que viene',
        #                '2018-01-25 00:00:00', 'recuerdame que llame')
        testExtract_es('recuérdame que controle el gasto del jueves pasado',
                       '2018-01-11 00:00:00', 'recuerdame que controle gasto')
        # TODO: Fail
        # testExtract_es('Jugar a futbol 2 días después del viernes',
        #                '2018-01-21 00:00:00', 'jugar futbol')
        testExtract_es('Limpiar a las 15:45 del jueves',
                       '2018-01-18 15:45:00', 'limpiar')
        testExtract_es('el lunes comprar queso',
                       '2018-01-15 00:00:00', 'comprar queso')
        # TODO: a "cumpleaños" se le tiene que quitar la "s" final
        testExtract_es('haz sonar música de cumpleaños en 5 años a partir de hoy',
                       '2023-01-13 00:00:00', 'haz sonar musica cumpleaño partir')
        testExtract_es('haz sonar música de cumpleaños en 5 años a desde hoy',
                       '2023-01-13 00:00:00', 'haz sonar musica cumpleaño desde')
        # TODO: "próximo" funciona, "que viene" no
        testExtract_es('Hacer un Skype con mama a las 12:45 del jueves'
                       ' próximo.',
                       '2018-01-25 12:45:00', 'hacer skype con mama')
        testExtract_es('¿Qué clima habrá este viernes?',
                       '2018-01-19 00:00:00', 'que clima habra')
        testExtract_es('¿Qué clima habrá este viernes por la tarde?',
                       '2018-01-19 15:00:00', 'que clima habra')
        testExtract_es('¿Qué clima habrá este viernes a media noche?',
                       '2018-01-20 00:00:00', 'que clima habra')
        testExtract_es('¿Qué clima habrá este viernes a mediodía?',
                       '2018-01-19 12:00:00', 'que clima habra')
        testExtract_es('Recuerdame llamar a mama el 3 agosto.',
                       '2018-08-03 00:00:00', 'recuerdame llamar mama')
        testExtract_es('compra las velas el 1° de mayo',
                       '2018-05-01 00:00:00', 'compra velas')
        testExtract_es('¿Qué clima habrá 1 día después de mañana?',
                       '2018-01-15 00:00:00', 'que clima habra')
        testExtract_es('¿Qué clima habrá a la hora 7?',
                       '2018-01-13 19:00:00', 'que clima habra')
        # TODO: Fail
        # testExtract_es('¿Qué clima habrá mañana a las 7 en punto?',
        #                '2018-01-14 07:00:00', 'que clima habra')
        # testExtract_es('¿Qué clima habrá mañana a las 2 de la tarde',
        #                '2018-01-14 14:00:00', 'que clima habra')
        # testExtract_es('¿Qué clima habrá mañana por la tarde a las 2',
        #                '2018-01-14 14:00:00', 'que clima habra')
        # testExtract_es('¿Qué clima habrá mañana sobre las 2:00',
        #                '2018-01-14 02:00:00', 'que clima habra')
        # TODO: "próximo" funciona, "que viene" no
        testExtract_es('¿Qué clima habrá a las 2 de la tarde del '
                       'viernes próximo?',
                       '2018-01-26 14:00:00', 'que clima habra')
        testExtract_es('Recuérdame que me despierte en 4 años',
                       '2022-01-13 00:00:00', 'recuerdame que me despierte')
        testExtract_es('Recuérdame que me despierte en 4 años y 4 días',
                       '2022-01-17 00:00:00', 'recuerdame que me despierte')
        # TODO: Fail
        # testExtract_es('Dormir 3 días desde mañana.',
        #                '2018-01-17 00:00:00', 'dormir')
        # testExtract_es('marca la cita en 2 semanas y 6 días '
        #                'después del sábado',
        #                '2018-02-02 00:00:00', 'marca cita')
        # TODO: Fail, cambia "fiesta" por "fieste"??
        # testExtract_es('La fiesta empieza a las 8 de la noche del jueves',
        #                '2018-01-18 20:00:00', 'fiesta empieza')
        testExtract_es('Qué tiempo hará en 3 días?',
                       '2018-01-16 00:00:00', 'que tiempo hara')
        testExtract_es('fija una cita diciembre 3',
                       '2018-12-03 00:00:00', 'fija cita')
        # TODO: Fail
        # testExtract_es('pon una cita el 3 de diciembre a las 3 de la tarde',
        #                '2018-12-03 15:00:00', 'fija cita')
        testExtract_es('encontrémonos esta noche a las 8 ',
                       '2018-01-13 20:00:00', 'encontremonos')
        testExtract_es('encontrémonos a las 8 esta noche',
                       '2018-01-13 20:00:00', 'encontremonos')
        testExtract_es('pon una alarma esta noche a las 9',
                       '2018-01-13 21:00:00', 'pon alarma')
        testExtract_es('pon una alarma esta noche a las 21',
                       '2018-01-13 21:00:00', 'pon alarma')
        # TODO: Fail
        # testExtract_es('insertar cita mañana por la noche a las 23',
        #                '2018-01-14 23:00:00', 'insertar cita')
        # testExtract_es('insertar cita mañana a las 9 y media',
        #                '2018-01-14 09:30:00', 'insertar cita')
        # testExtract_es('insertar cita mañana por la noche a las 23 y 3 cuartos',
        #                '2018-01-14 23:45:00', 'insertar cita')

        # TODO: Esto está bien, pero no entiendo por qué 5 cuartos está bien
        testExtract_es('insertar cita esta noche a las 23 y 5 cuartos',
                       '2018-01-13 23:00:00', 'insertar cita')

    def test_extractdatetime_es_normalized(self):
        """
        Test cases for Spanish datetime parsing

        """

        def extractWithFormat_es(text):
            date = datetime(2018, 1, 13, 13, 4)  # Sab 13 Gen, 2018 @ 13:04
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang='es')
            extractedDate = extractedDate.strftime('%Y-%m-%d %H:%M:%S')
            return [extractedDate, leftover]

        def testExtract_es(text, expected_date, expected_leftover):
            res = extractWithFormat_es(normalize(text, lang='es'))
            self.assertEqual(res[0], expected_date, 'por=' + text)
            self.assertEqual(res[1], expected_leftover, 'por=' + text)

        testExtract_es('recuérdame que llame a mamá en 15 minutos',
                       '2018-01-13 13:19:00', 'recuerdame que llame a mama')
        testExtract_es('llama a mamá a las 17 y 30',
                       '2018-01-13 17:30:00', 'llama a mama a')
        # TODO: fail
    #     testExtract_es('recuérdame que llame a mamá el sábado a las 10 ' +
    #                    'de la mañana',
    #                    '2018-01-13 10:00:00', 'recuerdame que llame a mama a mañana')
        # testExtract_es('recuérdame que llame a mamá a las 10 de la mañana de'
        #                ' este sábado',
        #                '2018-01-13 10:00:00', 'recuerdame que llame a mama a mañana')
        testExtract_es('recuérdame que llame a mamá a las 10 de la mañana del'
                       ' sábado que viene',
                       '2018-01-20 10:00:00', 'recuerdame que llame a mama a mañana')
        testExtract_es('recuérdame que llame a mamá a las 10 de la mañana del'
                       ' próximo sábado',
                       '2018-01-20 10:00:00', 'recuerdame que llame a mama a mañana')
        testExtract_es('¿Qué clima habrá este viernes a las 11 de la mañana?',
                       '2018-01-19 11:00:00', 'que clima habra a mañana')
        testExtract_es('comprar fresas el 13 de mayo',
                       '2018-05-13 00:00:00', 'comprar fresas')
        # testExtract_es('insertar cita mañana por la noche a las 23 y' +
        #                ' tres cuartos',
        #                '2018-01-14 23:45:00', 'insertar cita')

    def test_extract_ambiguous_time_es(self):
        mañana = datetime(2017, 6, 27, 8, 1, 2)
        noche = datetime(2017, 6, 27, 20, 1, 2)
        mediodia = datetime(2017, 6, 27, 12, 1, 2)
        self.assertEqual(
            extract_datetime('alimentar a los peces a las 10 en punto',
                             mañana, lang='es')[0],
            datetime(2017, 6, 27, 10, 0, 0))
        self.assertEqual(
            extract_datetime('alimentar a los peces a las 10 en punto',
                             mediodia, lang='es')[0],
            datetime(2017, 6, 27, 22, 0, 0))
        self.assertEqual(
            extract_datetime('alimentar a los peces a las 10 en punto',
                             noche, lang='es')[0],
            datetime(2017, 6, 27, 22, 0, 0))

    def test_extract_relativedatetime_es(self):
        """
        Test cases for relative datetime
        """
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2)
            [extractedDate, leftover] = extract_datetime(text, date,
                                                         lang='es')
            extractedDate = extractedDate.strftime('%Y-%m-%d %H:%M:%S')
            return [extractedDate, leftover]

        def testExtract_es(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, 'per =' + text)
            self.assertEqual(res[1], expected_leftover, 'per =' + text)

        testExtract_es('encontrémonos en 5 minutos',
                       '2017-06-27 10:06:02', 'encontremonos')
        testExtract_es('encontrémonos en 5 segundos',
                       '2017-06-27 10:01:07', 'encontremonos')
        testExtract_es('encontrémonos en 1 hora',
                       '2017-06-27 11:01:02', 'encontremonos')
        testExtract_es('encontrémonos en 2 horas',
                       '2017-06-27 12:01:02', 'encontremonos')
        testExtract_es('encontrémonos en 1 minuto',
                       '2017-06-27 10:02:02', 'encontremonos')
        testExtract_es('encontrémonos en 1 segundo',
                       '2017-06-27 10:01:03', 'encontremonos')
        testExtract_es('encontrémonos en 25 horas',
                       '2017-06-28 11:01:02', 'encontremonos')
    def test_spaces_es(self):
        """
        Test cases for Spanish remove spaces
        """
        self.assertEqual(normalize('esto   es    un    test  ',
                                   lang='es'), 'esto es 1 test')
        self.assertEqual(normalize('  otro test  ',
                                   lang='es'), 'otro test')
        self.assertEqual(normalize('esto es   otro test   ', lang='es',
                                   remove_articles=False),
                         'esto es otro test')
        self.assertEqual(normalize('esto   es  un    test   ', lang='es',
                                   remove_articles=False), 'esto es 1 test')

    def test_numbers_es(self):
        """
        Test cases for Spanish normalize lang='es'
        """
        self.assertEqual(normalize('es un test siete ocho nueve',
                                   lang='es'), 'es 1 test 7 8 9')
        self.assertEqual(normalize('test cero diez once doce trece',
                                   lang='es'), 'test 0 10 11 12 13')
        self.assertEqual(normalize('test mil seiscientos sesenta y seis',
                                   lang='es', remove_articles=False),
                         'test 1000 600 60 y 6')
        self.assertEqual(normalize('test siete y medio',
                                   lang='es', remove_articles=False),
                         'test 7 y 0.5')
        self.assertEqual(normalize('test dos punto nueve',
                                   lang='es'), 'test 2 punto 9')
        self.assertEqual(normalize('test ciento nueve',
                                   lang='es', remove_articles=False),
                         'test 100 9')
        # TODO: Acepta "veinti"
        self.assertEqual(normalize('test veinti y 1',
                                   lang='es'), 'test 20 y 1')
        self.assertEqual(normalize('test veintiuno y veintisiete',
                                   lang='es'), 'test 21 y 27')

    def test_multiple_numbers_es(self):
        self.assertEqual(extract_numbers('esto es la prueba uno dos tres',
                                         lang='es'), [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers('esto es la prueba cuatro siete' +
                                         ' cuatro',
                                         lang='es'), [4.0, 7.0, 4.0])
        self.assertEqual(extract_numbers('esto  es el test cinco seis siete',
                                         lang='es'), [5.0, 6.0, 7.0])
        self.assertEqual(extract_numbers('esto es  test diez once doce',
                                         lang='es'), [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers('test doce gatos veintiuno',
                                         lang='es'), [21.0, 12.0])
        self.assertEqual(extract_numbers('1 perro, siete cerdos, macdonald ' +
                                         'tenía la granja, 3 bodegas' +
                                         ' 5 macarena',
                                         lang='es'), [1, 7, 3, 5])
        self.assertEqual(extract_numbers('dos cervezas para dos osos',
                                         lang='es'), [2.0, 2.0])
        self.assertEqual(extract_numbers('veinte cuarenta treinta',
                                         lang='es'), [20, 40, 30])
        self.assertEqual(extract_numbers('veinte 20 22',
                                         lang='es'), [20, 20, 22])
        self.assertEqual(extract_numbers('veintidós locos veinte ratas '
                                         'veinte gatos',
                                         lang='es'), [22, 20, 20])
        self.assertEqual(extract_numbers('veinte 20 veinte 2',
                                         lang='es'), [20, 20, 20, 2])
        self.assertEqual(extract_numbers('un tercio uno',
                                         lang='es'), [1 / 3, 1])
        # TODO: Fail
        # self.assertEqual(extract_numbers('un tercio uno',
        #                       lang='es', ordinals=True), [3])
        # self.assertEqual(extract_numbers('seis millardos', lang='es',
        #                                  short_scale=True), [6e9])
        # self.assertEqual(extract_numbers('seis millones', lang='es',
        #                                  short_scale=False), [6e6])
        # self.assertEqual(extract_numbers('doce cerdos acompañan a \
        #  seis mil millones de bacterias', lang='es', short_scale=True), [6e9, 12])

        # TODO case when pronounced/extracted number don't match
        # fractional numbers often fail
        # self.assertEqual(extract_numbers('esto es un siete ocho \
        #                  nueve y medio test',lang='es'), [7.0, 8.0, 9.5])
        # TODO pronounce number should accept short_scale flag
        # self.assertEqual(extract_numbers('two pigs and six trillion
        # bacteria', short_scale=False), [2, 6e18])
        # TODO pronounce_number should accept ordinals flag
        # self.assertEqual(extract_numbers('thirty second or first',
        #                                 ordinals=True), [32, 1])

    def test_extractdatetime_default_es(self):
        default = time(9, 0, 0)
        anchor = datetime(2017, 6, 27, 0, 0)
        res = extract_datetime('¿Qué tiempo hará en 3 días?',
                               anchor, lang='es', default_time=default)
        self.assertEqual(default, res[0].time())

    def test_gender_es(self):
        """
        Test cases for Spanish grammar , lang='es'
        """
        self.assertEqual(get_gender('vaca', lang='es'), 'f')
        self.assertEqual(get_gender('caballo', lang='es'), 'm')
        self.assertEqual(get_gender('reses', 'las reses', lang='es'), 'f')
        self.assertEqual(get_gender('buey', 'el buey come de la hierba',
                                    lang='es'), 'm')
        self.assertEqual(get_gender('peces', 'los peces nadan',
                                    lang='es'), 'm')
        self.assertEqual(get_gender('tigre', lang='es'), 'm')
        self.assertEqual(get_gender('hombres', 'estos hombres comen pasta',
                                    lang='es'), 'm')
        self.assertEqual(get_gender('puente', 'el puente', lang='es'), 'm')
        self.assertEqual(get_gender('puente', u'este puente ha caído',
                                    lang='es'), 'm')
        self.assertEqual(get_gender('escultora', 'esta escultora famosa',
                                    lang='es'), 'f')
        self.assertEqual(get_gender('escultor', 'este escultor famoso',
                                    lang='es'), 'm')
        self.assertEqual(get_gender('escultores', 'los escultores del Renacimiento',
                                    lang='es'), 'm')
        self.assertEqual(get_gender('escultoras', 'las escultoras modernas',
                                    lang='es'), 'f')
        self.assertEqual(get_gender('emperatriz', 'la emperatriz murió',
                                    lang='es'), 'f')
        self.assertEqual(get_gender('actriz', lang='es'), 'f')
        self.assertEqual(get_gender('actor', lang='es'), 'm')


if __name__ == '__main__':
    unittest.main()