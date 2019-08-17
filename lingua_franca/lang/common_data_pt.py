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
from collections import OrderedDict

# Undefined articles ["um", "uma", "uns", "umas"] can not be supressed,
# in PT, "um cavalo" means "a horse" or "one horse".

_PT_ARTICLES = {"o", "a", "os", "as"}

_PT_NUMBERS = {
    "zero": 0,
    "um": 1,
    "uma": 1,
    "uns": 1,
    "umas": 1,
    "primeiro": 1,
    "segundo": 2,
    "terceiro": 3,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    u"três": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14,
    "quinze": 15,
    "dezasseis": 16,
    "dezassete": 17,
    "dezoito": 18,
    "dezanove": 19,
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
    "cem": 100,
    "cento": 100,
    "duzentos": 200,
    "duzentas": 200,
    "trezentos": 300,
    "trezentas": 300,
    "quatrocentos": 400,
    "quatrocentas": 400,
    "quinhentos": 500,
    "quinhentas": 500,
    "seiscentos": 600,
    "seiscentas": 600,
    "setecentos": 700,
    "setecentas": 700,
    "oitocentos": 800,
    "oitocentas": 800,
    "novecentos": 900,
    "novecentas": 900,
    "mil": 1000}

_FRACTION_STRING_PT = {
    2: 'meio',
    3: u'terço',
    4: 'quarto',
    5: 'quinto',
    6: 'sexto',
    7: u'sétimo',
    8: 'oitavo',
    9: 'nono',
    10: u'décimo',
    11: 'onze avos',
    12: 'doze avos',
    13: 'treze avos',
    14: 'catorze avos',
    15: 'quinze avos',
    16: 'dezasseis avos',
    17: 'dezassete avos',
    18: 'dezoito avos',
    19: 'dezanove avos',
    20: u'vigésimo',
    30: u'trigésimo',
    100: u'centésimo',
    1000: u'milésimo'
}

_NUM_STRING_PT = {
    0: 'zero',
    1: 'um',
    2: 'dois',
    3: 'três',
    4: 'quatro',
    5: 'cinco',
    6: 'seis',
    7: 'sete',
    8: 'oito',
    9: 'nove',
    10: 'dez',
    11: 'onze',
    12: 'doze',
    13: 'treze',
    14: 'catorze',
    15: 'quinze',
    16: 'dezasseis',
    17: 'dezassete',
    18: 'dezoito',
    19: 'dezanove',
    20: 'vinte',
    30: 'trinta',
    40: 'quarenta',
    50: 'cinquenta',
    60: 'sessenta',
    70: 'setenta',
    80: 'oitenta',
    90: 'noventa'
}

# split sentence parse separately and sum ( 2 and a half = 2 + 0.5 )
_FRACTION_MARKER_PT = {"e"}
# for non english speakers,  "X Y avos" means X / Y ,  Y must be > 10
_SUFFIX_FRACTION_MARKER_PT = {"avos"}
# mean you should sum the next number , equivalent to "and", i.e, "two thousand and one"
_SUM_MARKER_PT = {"e"}
# decimal marker ( 1 point 5 = 1 + 0.5)
_DECIMAL_MARKER_PT = {"ponto", "virgula", "vírgula"}

# negate next number (-2 = 0 - 2)
_NEGATIVES_PT = {"menos"}
# negate previous number, "2 negative" -> -2
_NEGATIVE_SUFFIX_MARKER_PT = {"negativo", "negativos"}

# _LONG_ORDINAL_PT, _LONG_SCALE_PT, _SHORT_SCALE_PT, _SHORT_ORDINAL_PT
_LONG_SCALE_PT = OrderedDict([
    (100, 'cem'),
    (1000, 'mil'),
    (1000000, 'milhão'),
    (1e12, "bilião"),
    (1e18, 'trilião'),
    (1e24, "quadrilião"),
    (1e30, "quintilião"),
    (1e36, "sextilião"),
    (1e42, "septilião"),
    (1e48, "octilião"),
    (1e54, "nonilião"),
    (1e60, "decilião"),
    (1e66, "undecilião"),
    (1e72, "duodecilião"),
    (1e78, "tredecilião"),
    (1e84, "quattuordecilião"),
    (1e90, "quinquadecilião"),
    (1e96, "sedecilião"),
    (1e102, "septendecilião"),
    (1e108, "octodecilião"),
    (1e114, "novendecilião"),
    (1e120, "vigintilião"),
    (1e306, "unquinquagintilião"),
    (1e312, "duoquinquagintilião"),
    (1e336, "sesquinquagintilião"),
    (1e366, "unsexagintilião")
])

_SHORT_SCALE_PT = OrderedDict([
    (100, 'cem'),
    (1000, 'mil'),
    (1000000, 'milhão'),
    (1e9, "bilião"),
    (1e12, 'trilião'),
    (1e15, "quadrilião"),
    (1e18, "quintilião"),
    (1e21, "sextilião"),
    (1e24, "septilião"),
    (1e27, "octilião"),
    (1e30, "nonilião"),
    (1e33, "decilião"),
    (1e36, "undecilião"),
    (1e39, "duodecilião"),
    (1e42, "tredecilião"),
    (1e45, "quattuordecilião"),
    (1e48, "quinquadecilião"),
    (1e51, "sedecilião"),
    (1e54, "septendecilião"),
    (1e57, "octodecilião"),
    (1e60, "novendecilião"),
    (1e63, "vigintilião"),
    (1e66, "unvigintilião"),
    (1e69, "uuovigintilião"),
    (1e72, "tresvigintilião"),
    (1e75, "quattuorvigintilião"),
    (1e78, "quinquavigintilião"),
    (1e81, "qesvigintilião"),
    (1e84, "septemvigintilião"),
    (1e87, "octovigintilião"),
    (1e90, "novemvigintilião"),
    (1e93, "trigintilião"),
    (1e96, "untrigintilião"),
    (1e99, "duotrigintilião"),
    (1e102, "trestrigintilião"),
    (1e105, "quattuortrigintilião"),
    (1e108, "quinquatrigintilião"),
    (1e111, "sestrigintilião"),
    (1e114, "septentrigintilião"),
    (1e117, "octotrigintilião"),
    (1e120, "noventrigintilião"),
    (1e123, "quadragintilião"),
    (1e153, "quinquagintilião"),
    (1e183, "sexagintilião"),
    (1e213, "septuagintilião"),
    (1e243, "octogintilião"),
    (1e273, "nonagintilião"),
    (1e303, "centilião"),
    (1e306, "uncentilião"),
    (1e309, "duocentilião"),
    (1e312, "trescentilião"),
    (1e333, "decicentilião"),
    (1e336, "undecicentilião"),
    (1e363, "viginticentilião"),
    (1e366, "unviginticentilião"),
    (1e393, "trigintacentilião"),
    (1e423, "quadragintacentilião"),
    (1e453, "quinquagintacentilião"),
    (1e483, "sexagintacentilião"),
    (1e513, "septuagintacentilião"),
    (1e543, "ctogintacentilião"),
    (1e573, "nonagintacentilião"),
    (1e603, "ducentilião"),
    (1e903, "trecentilião"),
    (1e1203, "quadringentilião"),
    (1e1503, "quingentilião"),
    (1e1803, "sescentilião"),
    (1e2103, "septingentilião"),
    (1e2403, "octingentilião"),
    (1e2703, "nongentilião"),
    (1e3003, "millinilião")
])

_ORDINAL_BASE_PT = {
    1: 'primeiro',
    2: 'segundo',
    3: 'terceiro',
    4: 'quarto',
    5: 'quinto',
    6: 'sixto',
    7: 'sétimo',
    8: 'oitavo',
    9: 'nono',
    10: 'décimo',
    20: 'vigésimo',
    30: 'trigésimo',
    40: "quadragésimo",
    50: "quinquagesimo",
    60: "sextagésimo",
    70: "septagésimo",
    80: "octagésimo",
    90: "nonaésimo",
    10e3: "centésimo",
    1e3: "milésimo"
}

_SHORT_ORDINAL_PT = {
    1e6: "milionésimo",
    1e9: "bilionésimo",
    1e12: "trilionésimo",
    1e15: "quadrilionésimo",
    1e18: "quintilionésimo",
    1e21: "sextilionésimo",
    1e24: "septilionésimo",
    1e27: "octilionésimo",
    1e30: "nonilionésimo",
    1e33: "decilionésimo"
    # TODO > 1e-33
}
_SHORT_ORDINAL_PT.update(_ORDINAL_BASE_PT)

_LONG_ORDINAL_PT = {
    1e6: "milionésimo",
    1e12: "bilionésimo",
    1e18: "trilionésimo",
    1e24: "quadrilionésimo",
    1e30: "quintilionésimo",
    1e36: "sextilionésimo",
    1e42: "septilionésimo",
    1e48: "octilionésimo",
    1e54: "nonilionésimo",
    1e60: "decilionésimo"
    # TODO > 1e60
}
_LONG_ORDINAL_PT.update(_ORDINAL_BASE_PT)
