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

# NOTE: This file as no use yet. It needs to be called from other functions

from collections import OrderedDict

# Undefined articles ["un", "unos", "una", "unas"] can not be supressed,
# in ES, "un cavallo" means "a horse" or "one horse".

_ARTICLES_ES = {'el', 'la', 'los', 'las'}

# word rules for gender
# TODO: review rules to see exceptions
_FEMALE_ENDINGS_ES = ["a", "as"]
_MALE_ENDINGS_ES = ["o", "os"]

# special cases, word lookup for words not covered by above rule
_GENDERS_ES = {
    "mujer": "f",
    "mujeres": "f",
    "madre": "f",
    "hombre": "m",
    "padre": "m"
}

# context rules for gender
_MALE_DETERMINANTS_ES = ["lo", "los", "este", "estos", "ese", "esos"]
_FEMALE_DETERMINANTS_ES = ["la", "las", "esta", "estas", "esa", "esas"]


_NUMBERS_ES = {
    "cero": 0,
    "un": 1,
    "uno": 1,
    "una": 1,
    "primero": 1,
    "segundo": 2,
    "tercero": 3,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciséis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
    "veinte": 20,
    "veintiuno": 21,
    "veintidós": 22,
    "veintitrés": 23,
    "veinticuatro": 24,
    "veinticinco": 25,
    "veintiséis": 26,
    "veintisiete": 27,
    "veintiocho": 28,
    "veintinueve": 29,
    "treinta": 30,
    "cuarenta": 40,
    "cinquenta": 50,
    "sesenta": 60,
    "setenta": 70,
    "ochenta": 80,
    "noventa": 90,
    "cien": 100,
    "ciento": 100,
    "doscientos": 200,
    "doscientas": 200,
    "trecientos": 300,
    "trecientas": 300,
    "cuatrocientos": 400,
    "cuatrocientas": 400,
    "quinientos": 500,
    "quinientas": 500,
    "seiscientos": 600,
    "seiscientas": 600,
    "setecientos": 700,
    "setecientas": 700,
    "ochocientos": 800,
    "ochocientas": 800,
    "novecientos": 900,
    "novecientas": 900,
    "mil": 1000
    }

# Fractions can be noun (e.g: 1/2, 3/4) or adjectives (e.g.: 1/4 part of 
# something). As a noun is commonly expressed as masculine while when is an
# adjective is always femenine 
# https://espanol.lingolia.com/es/vocabulario/numeros-fechas-horas/fracciones
# Because the femenine particle (adjective) can be extrapolated thanks to the
# article, we put here just the noun.
# As a noun, fractions for décimas, centésimas, milésimas, cienmilésimas, etc
# are expressed in femenine in Spain, while in some Latam countries are 
# expressed in masculine.
_FRACTION_STRING_ES = {
    2: 'medio',
    3: 'tercio',
    4: 'cuarto',
    5: 'quinto',
    6: 'sexto',
    7: 'séptimo',
    8: 'octavo',
    9: 'noveno',
    10: 'décimo',
    11: 'onceavo',
    12: 'doceavo',
    13: 'treceavo',
    14: 'catorceavo',
    15: 'quinceavo',
    16: 'dieciseisavo',
    17: 'diecisieteavo',
    18: 'dieciochoavo',
    19: 'diecinueveavo',
    20: 'veinteavo',
    30: 'treintavo',
    100: 'centésima',
    1000: 'milésima'
}


_NUM_STRING_ES = {
    0: 'cero',
    1: 'uno',
    2: 'dos',
    3: 'tres',
    4: 'cuatro',
    5: 'cinco',
    6: 'seis',
    7: 'siete',
    8: 'ocho',
    9: 'nueve',
    10: 'diez',
    11: 'once',
    12: 'doce',
    13: 'trece',
    14: 'catorce',
    15: 'quince',
    16: 'dieciséis',
    17: 'diecisete',
    18: 'dieciocho',
    19: 'diecinueve',
    20: 'veinte',
    21: 'veintiuno',
    22: 'veintidos',
    23: 'veintitres',
    24: 'veinticuatro',
    25: 'veinticinco',
    26: 'veintiséis',
    27: 'veintisiete',
    28: 'veintiocho',
    29: 'veintinueve',
    30: 'treinta',
    40: 'cuarenta',
    50: 'cincuenta',
    60: 'sesenta',
    70: 'setenta',
    80: 'ochenta',
    90: 'noventa'
}

# split sentence parse separately and sum ( 2 and a half = 2 + 0.5 )
_FRACTION_MARKER_ES = {"y"}
# for non english speakers,  "X Y avos" means X / Y ,  Y must be > 10
_SUFFIX_FRACTION_MARKER_ES = {"avos"}
# mean you should sum the next number , equivalent to "and", i.e, "two thousand and one"
# WARNING: In spanish we use this ONLY between tens and units (i.e. treinta y seis)
_SUM_MARKER_ES = {"y"}
# decimal marker ( 1 point 5 = 1 + 0.5)
# WARNING: In proper Spanish, the only valid term is "coma", we put here "punto" for
# compatibility, but is wrong, as the decimals are written with comma, so even when 
# we read loud a text in english like 0.5 we said "cero coma cinco"
_DECIMAL_MARKER_ES = {"coma", "punto"}

# negate next number (-2 = 0 - 2)
_NEGATIVES_ES = {"menos"}
# negate previous number, "2 negative" -> -2
_NEGATIVE_SUFFIX_MARKER_ES = {"negativo", "negativos"}

# Long scale is the default scale on Spain
# https://www.grobauer.at/es_eur/zahlnamen.php
_LONG_SCALE_ES = OrderedDict([
    (100, 'centena'),
    (1000, 'millar'),
    (1000000, 'millón'),
    (1e9, "millardo"),
    (1e12, "billón"),
    (1e18, 'trillón'),
    (1e24, "cuatrillón"),
    (1e30, "quintillón"),
    (1e36, "sextillón"),
    (1e42, "septillón"),
    (1e48, "octillón"),
    (1e54, "nonillón"),
    (1e60, "decillón"),
    (1e66, "undecillón"),
    (1e72, "duodecillón"),
    (1e78, "tredecillón"),
    (1e84, "cuatrodecillón"),
    (1e90, "quindecillón"),
    (1e96, "sexdecillón"),
    (1e102, "septendecillón"),
    (1e108, "octodecillón"),
    (1e114, "novendecillón"),
    (1e120, "vigintillón"),
    (1e306, "unquinquagintillón"),
    (1e312, "duoquinquagintillón"),
    (1e336, "sexquinquagintillón"),
    (1e366, "unsexagintillón")
])

# Short scale is the default scale on America
_SHORT_SCALE_ES = OrderedDict([
    (100, 'centena'),
    (1000, 'millar'),
    (1000000, 'millón'),
    (1e9, "billón"),
    (1e12, 'trillón'),
    (1e15, "cuatrillón"),
    (1e18, "quintillón"),
    (1e21, "sextillón"),
    (1e24, "septillón"),
    (1e27, "octillón"),
    (1e30, "nonillón"),
    (1e33, "decillón"),
    (1e36, "undecillón"),
    (1e39, "duodecillón"),
    (1e42, "tredecillón"),
    (1e45, "cuatrodecillón"),
    (1e48, "quindecillón"),
    (1e51, "sexdecillón"),
    (1e54, "septendecillón"),
    (1e57, "octodecillón"),
    (1e60, "novendecillón"),
    (1e63, "vigintillón"),
    (1e66, "unvigintillón"),
    (1e69, "uuovigintillón"),
    (1e72, "tresvigintillón"),
    (1e75, "quattuorvigintillón"),
    (1e78, "quinquavigintillón"),
    (1e81, "qesvigintillón"),
    (1e84, "septemvigintillón"),
    (1e87, "octovigintillón"),
    (1e90, "novemvigintillón"),
    (1e93, "trigintillón"),
    (1e96, "untrigintillón"),
    (1e99, "duotrigintillón"),
    (1e102, "trestrigintillón"),
    (1e105, "quattuortrigintillón"),
    (1e108, "quinquatrigintillón"),
    (1e111, "sestrigintillón"),
    (1e114, "septentrigintillón"),
    (1e117, "octotrigintillón"),
    (1e120, "noventrigintillón"),
    (1e123, "quadragintillón"),
    (1e153, "quinquagintillón"),
    (1e183, "sexagintillón"),
    (1e213, "septuagintillón"),
    (1e243, "octogintillón"),
    (1e273, "nonagintillón"),
    (1e303, "centillón"),
    (1e306, "uncentillón"),
    (1e309, "duocentillón"),
    (1e312, "trescentillón"),
    (1e333, "decicentillón"),
    (1e336, "undecicentillón"),
    (1e363, "viginticentillón"),
    (1e366, "unviginticentillón"),
    (1e393, "trigintacentillón"),
    (1e423, "quadragintacentillón"),
    (1e453, "quinquagintacentillón"),
    (1e483, "sexagintacentillón"),
    (1e513, "septuagintacentillón"),
    (1e543, "ctogintacentillón"),
    (1e573, "nonagintacentillón"),
    (1e603, "ducentillón"),
    (1e903, "trecentillón"),
    (1e1203, "quadringentillón"),
    (1e1503, "quingentillón"),
    (1e1803, "sexcentillón"),
    (1e2103, "septingentillón"),
    (1e2403, "octingentillón"),
    (1e2703, "nongentillón"),
    (1e3003, "millinillón")
])

# TODO: female forms.
_ORDINAL_BASE_ES = {
    1: 'primero',
    2: 'segundo',
    3: 'tercero',
    4: 'cuarto',
    5: 'quinto',
    6: 'sexto',
    7: 'séptimo',
    8: 'octavo',
    9: 'noveno',
    10: 'décimo',
    11: 'undécimo',
    12: 'duodécimo',
    13: 'decimotercero',
    14: 'decimocuarto',
    15: 'decimoquinto',
    16: 'decimosexto',
    17: 'decimoséptimo',
    18: 'decimoctavo',
    19: 'decimonoveno',
    20: 'vigésimo',
    30: 'trigésimo',
    40: "cuadragésimo",
    50: "quincuagésimo",
    60: "sexagésimo",
    70: "septuagésimo",
    80: "octogésimo",
    90: "nonagésimo",
    10e3: "centésimó",
    1e3: "milésimo"
}


_SHORT_ORDINAL_ES = {
    1e6: "millonésimo",
    1e9: "milmillonésimo",
    1e12: "billonésimo",
    1e15: "milbillonésimo",
    1e18: "trillonésimo",
    1e21: "miltrillonésimo",
    1e24: "cuatrillonésimo",
    1e27: "milcuatrillonésimo",
    1e30: "quintillonésimo",
    1e33: "milquintillonésimo"
    # TODO > 1e-33
}
_SHORT_ORDINAL_ES.update(_ORDINAL_BASE_ES)


_LONG_ORDINAL_ES = {
    1e6: "millonésimo",
    1e12: "billionth",
    1e18: "trillonésimo",
    1e24: "cuatrillonésimo",
    1e30: "quintillonésimo",
    1e36: "sextillonésimo",
    1e42: "septillonésimo",
    1e48: "octillonésimo",
    1e54: "nonillonésimo",
    1e60: "decillonésimo"
    # TODO > 1e60
}
_LONG_ORDINAL_ES.update(_ORDINAL_BASE_ES)
