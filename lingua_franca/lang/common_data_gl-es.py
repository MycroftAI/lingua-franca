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


_ARTICLES_GL-ES = {'o', 'a', 'os', 'as'}

_NUM_STRING_GL-ES = {
    0: 'cero',
    1: 'un',
    2: 'dous',
    3: 'tres',
    4: 'catro',
    5: 'cinco',
    6: 'seis',
    7: 'sete',
    8: 'oito',
    9: 'nove',
    10: 'dez',
    11: 'once',
    12: 'doce',
    13: 'trece',
    14: 'catorce',
    15: 'quince',
    16: 'dezaseis',
    17: 'dezasete',
    18: 'dezaoito',
    19: 'dezanove',
    20: 'vinte',
    30: 'trinta',
    40: 'corenta',
    50: 'cincuenta',
    60: 'sesenta',
    70: 'setenta',
    80: 'oitenta',
    90: 'noventa'
}

_STRING_NUM_GL-ES = {
    "cero": 0,
    "un": 1,
    "unha": 1,
    "dous": 2,
    "tres": 3,
    "catro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dezaseis": 16,
    "dezasete": 17,
    "dezaoito": 18,
    "dezanove": 19,
    "vinte": 20,
    "vinte e un": 21,
    "vinte e dous": 22,
    "vinte e tres": 23,
    "vinte e catro": 24,
    "vinte e cinco": 25,
    "vinte e seis": 26,
    "vinte e sete": 27,
    "vinte e oito": 28,
    "vinte e nove": 29,
    "trinta": 30,
    "corenta": 40,
    "cincuenta": 50,
    "sesenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
    "cen": 100,
    "cento": 100,
    "douscentos": 200,
    "duascentas": 200,
    "trescentos": 300,
    "trescentas": 300,
    "catrocentos": 400,
    "catrocentas": 400,
    "cincocentos": 500,
    "cincocentas": 500,
    "seiscentos": 600,
    "seiscentas": 600,
    "setecentos": 700,
    "setecentas": 700,
    "oitocentos": 800,
    "oitocentas": 800,
    "novecentos": 900,
    "novecentas": 900,
    "mil": 1000}


_FRACTION_STRING_GL-ES = {
    2: 'medio',
    3: 'terzo',
    4: 'cuarto',
    5: 'quinto',
    6: 'sexto',
    7: 'séptimo',
    8: 'oitavo',
    9: 'noveno',
    10: 'décimo',
    11: 'onceavo',
    12: 'doceavo',
    13: 'treceavo',
    14: 'catorceavo',
    15: 'quinceavo',
    16: 'dezaseisavo',
    17: 'dezaseteavo',
    18: 'dezaoitoavo',
    19: 'dezanoveavo',
    20: 'vinteavo'
}

# https://www.grobauer.at/es_eur/zahlnamen.php
_LONG_SCALE_GL-ES = OrderedDict([
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


_SHORT_SCALE_GL-ES = OrderedDict([
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
    (1e69, "unovigintillón"),
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
    (1e543, "octogintacentillón"),
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
_ORDINAL_STRING_BASE_GL-ES = {
    1: 'primeiro',
    2: 'segundo',
    3: 'terceiro',
    4: 'cuarto',
    5: 'quinto',
    6: 'sexto',
    7: 'séptimo',
    8: 'oitavo',
    9: 'noveno',
    10: 'décimo',
    11: 'undécimo',
    12: 'duodécimo',
    13: 'decimoterceiro',
    14: 'decimocuarto',
    15: 'decimoquinto',
    16: 'decimosexto',
    17: 'decimoséptimo',
    18: 'decimoitavo',
    19: 'decimonoveno',
    20: 'vixésimo',
    30: 'trixésimo',
    40: "cuadraxésimo",
    50: "quincuaxésimo",
    60: "sexaxésimo",
    70: "septuaxésimo",
    80: "octoxésimo",
    90: "nonaxésimo",
    10e3: "centésimo",
    1e3: "milésimo"
}


_SHORT_ORDINAL_STRING_GL-ES = {
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
_SHORT_ORDINAL_STRING_GL-ES.update(_ORDINAL_STRING_BASE_GL-ES)


_LONG_ORDINAL_STRING_GL-ES = {
    1e6: "millonésimo",
    1e12: "billonésimo",
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
_LONG_ORDINAL_STRING_GL-ES.update(_ORDINAL_STRING_BASE_GL-ES)
