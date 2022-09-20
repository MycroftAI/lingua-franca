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
from dateutil import tz

from lingua_franca import load_language, unload_language, set_default_lang
from lingua_franca.internal import FunctionNotLocalizedError
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import get_gender
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize
from lingua_franca.lang.parse_syr import extract_datetime_syr
from lingua_franca.time import default_timezone


def setUpModule():
    load_language('syr')
    set_default_lang('syr')

def tearDownModule():
    unload_language('syr')

class TestNormalize(unittest.TestCase):

    def test_extract_number(self):
        self.assertEqual(extract_number("ܐܗܐ ܝܠܗ ܢܣܝܢܐ ܩܕܡܝܐ",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("ܐܗܐ ܝܠܗ ܢܣܝܢܐ ܬܪܝܢܐ"), 2)
        self.assertEqual(extract_number("ܐܗܐ ܝܠܗ ܢܣܝܢܐ ܪܒܝܥܝܐ"), 4)
        self.assertEqual(extract_number("ܬܠܬܐ ܟ̈ܣܐ"), 3)
        self.assertEqual(extract_number("ܚܕ ܘܦܠܓܐ ܟ̈ܣܐ"), 1.5)
        self.assertEqual(extract_number("ܥܣܪܝܢ ܘܬܪܝܢ"), 22)        
        self.assertEqual(extract_number("ܬܪܝܢܡܐܐ"), 200)
        self.assertEqual(extract_number("ܬܫܥܐ ܐܠܦܐ"), 9000)
        self.assertEqual(extract_number("ܐܠܦܐ ܘܚܡܫܡܐܐ"), 1500)
        self.assertEqual(extract_number("ܫܬܡܐܐ ܘܫܬܝܢ ܘܫܬܐ"), 666)
        self.assertEqual(extract_number("ܬܪܝܢ ܡܠܝܘܢܐ"), 2000000)
        self.assertEqual(extract_number("ܬܪܝܢ ܐܠܦܐ ܘܫܒܥܣܪ"), 2017)
        self.assertEqual(extract_number("ܫܬܥܣܪ ܐܠܦܐ ܘܡܐܐ ܘܚܡܫܥܣܪ"), 16115)
        self.assertEqual(extract_number("ܬܡܢܥܣܪ ܡܠܝܘܢܐ ܘܬܡܢܥܣܪ ܐܠܦܐ ܘܬܪܝܢܡܐܐ ܘܬܡܢܥܣܪ"), 18018218)
        self.assertEqual(extract_number("ܬܪܝܢ ܡܠܝܘܢܐ ܘܚܡܫܡܐܐ ܐܠܦܐ"), 2500000)

    def test_extract_duration_syr(self):
        self.assertEqual(extract_duration("10 ܪ̈ܦܦܐ"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 ܩܛܝܢ̈ܬܐ"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 ܫܥ̈ܐ"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 ܝܘܡܢ̈ܐ"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 ܫܒ̈ܘܥܐ"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("ܫܒܥܐ ܫܥ̈ܐ"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 ܪ̈ܦܦܐ"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("ܬܡܢܝܐ ܘܦܠܓܐ ܝܘܡܢ̈ܐ ܘܬܠܬܝܢ ܘܬܫܥܐ ܪ̈ܦܦܐ"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ ܩܐ ܬܠܬܝܢ ܩܛܝܢ̈ܬܐ ܐܚܪܢܐ"),
                         (timedelta(minutes=30), "ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ ܩܐ ܐܚܪܢܐ"))
        self.assertEqual(extract_duration("ܡܬܒ ܥܕܢܐ ܐܪܒܥܐ ܘܦܠܓܐ ܩܛܝܢ̈ܬܐ ܠܙܪܩܬܐ ܕܫܡܫܐ"),
                         (timedelta(minutes=4.5), "ܡܬܒ ܥܕܢܐ ܠܙܪܩܬܐ ܕܫܡܫܐ"))
        self.assertEqual(extract_duration("ܐܗܐ ܨܘܪܬܐ ܙܝܘܥܬܐ ܟܐ ܓܪܫ ܥܕܢܐ ܚܕ ܫܥܬܐ ܘܚܡܫܝܢ ܘܫܒܥܐ ܘܦܠܓܐ ܩܛܝܢ̈ܬܐ"),
                         (timedelta(hours=1, minutes=57.5),
                             "ܐܗܐ ܨܘܪܬܐ ܙܝܘܥܬܐ ܟܐ ܓܪܫ ܥܕܢܐ"))

    def test_extractdatetime_syr(self):

        def extractWithFormat(text):
        # BUG: Time is read as 2017-06-27 08:04:00 which is incorrect
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime_syr(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(text)
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("ܗܫܐ ܝܠܗ ܥܕܢܐ",
                    "2017-06-27 13:04:00", "ܝܠܗ ܥܕܢܐ")
        testExtract("ܚܕ ܪܦܦܐ ܝܬܝܪ",
                    "2017-06-27 13:04:01", "ܚܕ ܝܬܝܪ")
        testExtract("ܝܠܗ ܚܕ ܩܛܝܢܐ",
                    "2017-06-27 13:05:00", "ܚܕ")
        testExtract("ܬܪܝܢ ܩܛܝܢ̈ܬܐ",
                    "2017-06-27 13:06:00", "ܬܪܝܢ")
        testExtract("ܝܠܗ̇ ܥܕܢܐ ܚܫܝܚܬܐ",
                    "2017-06-27 15:04:00", "")
        testExtract("ܐܢܐ ܒܥܝܢ ܩܐ ܚܕ ܫܥܬܐ ܐܚܪܢܐ",
                    "2017-06-27 14:04:00", "ܐܢܐ ܒܥܝܢ ܩܐ ܐܚܪܢܐ")
        testExtract("1 ܪܦܦܐ ܐܚܪܢܐ",
                    "2017-06-27 13:04:01", "1 ܐܚܪܢܐ")
#        testExtract("2 ܪ̈ܦܦܐ ܐܚܪܢܐ",
#                    "2017-06-27 13:04:02", "")
#        testExtract("ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ ܩܐ ܚܕ ܩܛܝܢܐ ܒܬܪ",
#                    "2017-06-27 13:05:00", "ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ")
#        testExtract("ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ ܩܐ ܦܠܓܐ ܫܥܬܐ ܐܚܪܢܐ",
#                    "2017-06-27 13:34:00", "ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ")
#        testExtract("ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ ܩܐ ܚܡܫܐ ܝܘ̈ܡܬܐ ܒܬܪ",
#                    "2017-07-02 00:00:00", "ܡܬܒ ܡܐܢܐ ܙܒ̣ܢܢܝܐ")
#        testExtract("ܒܝܘܡܐ ܐܚܖܢܐ",
#                    "2017-06-29 00:00:00", "")
#        testExtract("ܡܘܕܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ ܒܡܚܪ؟",
#                    "2017-06-29 00:00:00", "ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ؟")
#        testExtract("ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ ܥܪܘܒܬܐ ܨܦܪܐ؟",
#                    "2017-06-30 08:00:00", "ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ؟")
#        testExtract("ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ ܒܡܚܪ؟",
#                    "2017-06-28 00:00:00", "ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ؟")
#        testExtract("ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ ܝܘܡܢܐ ܒܬܪ ܛܗܪܐ؟",
#                    "2017-06-27 15:00:00", "ܕܐܟܝ ܝܠܗ ܡܘܙܓܐ ܕܐܐܪ؟")
#        testExtract("ܕܟܪ ܩܖܝ ܩܐ ܝܡܝ ܒܬܡܢܝܐ ܫܒ̈ܘܥܐ ܘܬܪܝܢ ܝܘ̈ܡܬܐ",
#                    "2017-08-24 00:00:00", "ܕܟܪ ܩܖܝ ܩܐ ܝܡܝ")

#    def test_multiple_numbers(self):
#        self.assertEqual(extract_numbers("ܚܕ ܬܪܝܢ ܬܠܬܐ"),
#                         [1.0, 2.0, 3.0])

        # BUG: It is read as 10, 20, 3, 15, 16 as it fails to recognize ܐܠܦ̈ܐ ܘܫܬܝܢ
#        self.assertEqual(extract_numbers("ܥܣܪܐ ܥܣܪܝܢ ܬܠܬܐ ܚܡܫܥܣܪ ܐܠܦܐ ܘܫܬܝܢ ܫܬܥܣܪ"),
#                         [10, 20, 3, 15060, 16])
        
        


if __name__ == "__main__":
    unittest.main()
