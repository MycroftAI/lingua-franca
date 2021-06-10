#
# Copyright 2019 Mycroft AI Inc.
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

import unittest

from lingua_franca.lang.parse_common import Normalizer, tokenize, Token


class TestParseCommon(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(tokenize('One small step for man'),
                         [Token('One', 0), Token('small', 1), Token('step', 2),
                          Token('for', 3), Token('man', 4)])

        self.assertEqual(tokenize('15%'),
                         [Token('15', 0), Token('%', 1)])

        self.assertEqual(tokenize('I am #1'),
                         [Token('I', 0), Token('am', 1), Token('#', 2),
                          Token('1', 3)])

        self.assertEqual(tokenize('hashtag #1world'),
                         [Token('hashtag', 0), Token('#1world', 1)])

    def test_normalize(self):

        normalizer = Normalizer()
        self.assertEqual(normalizer.normalize('Set volume to 50%.'),
                         'Set volume to 50%.')

        self.assertEqual(normalizer.normalize('I am 100% sure.'), 
                         'I am 100% sure.')

        self.assertEqual(normalizer.normalize('Is current volume 42%?'),
                         'Is current volume 42%?')

        self.assertEqual(normalizer.normalize('42% is current volume!'),
                         '42% is current volume!')

        self.assertEqual(normalizer.normalize('It takes 12.34% of revenue.'),
                         'It takes 12.34% of revenue.')

        self.assertEqual(normalizer.normalize('Return on asset is 56.78%.'),
                         'Return on asset is 56.78%.')