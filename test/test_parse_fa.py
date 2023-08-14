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
from lingua_franca.time import default_timezone
from lingua_franca.parse import extract_datetime
from lingua_franca.parse import extract_duration
from lingua_franca.parse import extract_number, extract_numbers
from lingua_franca.parse import fuzzy_match
from lingua_franca.parse import get_gender
from lingua_franca.parse import match_one
from lingua_franca.parse import normalize


def setUpModule():
    # TODO spin off English tests
    load_language('fa')
    set_default_lang('fa')


def tearDownModule():
    unload_language('fa')


class TestNormalize(unittest.TestCase):
    
    def test_extract_number_ambiguous(self):
        # test explicit ordinals
        self.assertEqual(extract_number("این تست ۱ام هستش",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("این تست ۲ام هست",
                                        ordinals=False), 2)
        self.assertEqual(extract_number("این تست ۴ام است",
                                        ordinals=None), 4)
        self.assertEqual(extract_number(
            "این تست ۷ام هست", ordinals=True), 7)
        self.assertEqual(extract_number(
            "این تست ۷ام هست", ordinals=False), 7)
        self.assertTrue(extract_number("این تست چندم است") is False)
        self.assertEqual(extract_number("این تست ۲ام هست"), 2)
        self.assertEqual(extract_number("این تست ۳۱ام هست"), 31)

        # test non ambiguous ordinals
        self.assertEqual(extract_number("این تست اول هست",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("این تست یکم هست",
                                        ordinals=True), 1)
        self.assertEqual(extract_number("این تست اول هست",
                                        ordinals=False), False)
        self.assertEqual(extract_number("این تست اول هست",
                                        ordinals=None), False)

        # test ambiguous ordinal/fractional
        self.assertEqual(extract_number("این تست سوم هست",
                                        ordinals=True), 3.0)
        self.assertEqual(extract_number("این تست سوم هست",
                                        ordinals=False), False)
        self.assertEqual(extract_number("این تست سوم هست",
                                        ordinals=None), False)

        self.assertEqual(extract_number("یک سوم فنجان",
                                        ordinals=False), 1.0 / 3.0)
        self.assertEqual(extract_number("یک سوم فنجان",
                                        ordinals=True), 3)
        self.assertEqual(extract_number("یک سوم فنجان",
                                        ordinals=None), 1 / 3)

        # test plurals
        self.assertEqual(extract_number("۲ پنجم",
                                        ordinals=True), 5)
        self.assertEqual(extract_number("۲ پنجم",
                                        ordinals=False), 2 / 5)
        self.assertEqual(extract_number("۲ پنجم",
                                        ordinals=None), 2 / 5)

        self.assertEqual(extract_number("بیست و دو و سه پنجم"), 22.6)

        # test multiple ambiguous
        self.assertEqual(extract_number("ششم سوم", ordinals=None), False)
        self.assertEqual(extract_number("سی و دوم", ordinals=False), 30)
        self.assertEqual(extract_number("سی و دوم", ordinals=None), 30)
        self.assertEqual(extract_number("سی و دوم", ordinals=True), 32)

        # test big numbers / short vs long scale
        self.assertEqual(extract_number("این تست یک میلیاردم هست",
                                        ordinals=True), 1e09)
        self.assertEqual(extract_number("این تست یک میلیاردم هست",
                                        ordinals=None), 1e-9)

        self.assertEqual(extract_number("این تست یک میلیاردم هست",
                                        ordinals=False), 1e-9)
        self.assertEqual(extract_number("این تست یک میلیاردم هست",
                                        ordinals=True,
                                        short_scale=False), 1e9)
        self.assertEqual(extract_number("این تست یک میلیاردم هست",
                                        ordinals=None,
                                        short_scale=False), 1e-9)
        self.assertEqual(extract_number("این تست یک میلیاردم هست",
                                        short_scale=False), 1e-9)

    def test_extract_number(self):
        self.assertEqual(extract_number("این تست ۲ هست"), 2)
        self.assertEqual(extract_number("این تست شماره ۴ هستش"), 4)
        self.assertEqual(extract_number("سه فنجان"), 3)
        self.assertEqual(extract_number("یک سوم فنجان"), 1.0 / 3.0)
        self.assertEqual(extract_number("1/4 فنجان"), 0.25)
        self.assertEqual(extract_number("یک چهارم فنجان"), 0.25)
        self.assertEqual(extract_number("2/3 فنجان"), 2.0 / 3.0)
        # self.assertEqual(extract_number("یک فنجان و نیم"), 1.5)
        self.assertEqual(extract_number("یک و نیم فنجان"), 1.5)
        self.assertEqual(extract_number("بیست و دو"), 22)
        self.assertEqual(extract_number("دویست"), 200)
        self.assertEqual(extract_number("نه هزار"), 9000)
        self.assertEqual(extract_number("ششصد و شصت و شش"), 666)
        self.assertEqual(extract_number("دو میلیون"), 2000000)
        self.assertEqual(extract_number("دو میلیون و پانصد هزار تن فلز چرخان"), 2500000)
        self.assertEqual(extract_number("شش تریلیون"), 6000000000000.0)
        self.assertEqual(extract_number("شش تریلیون", short_scale=False),
                         6000000000000.0)
        self.assertEqual(extract_number("یک ممیز پنج"), 1.5)
        self.assertEqual(extract_number("سه ممیز چهارده"), 3.14)
        self.assertEqual(extract_number("سه ممیز بیست و سه"), 3.23)
        self.assertEqual(extract_number("دو دهم"), 0.2)
        self.assertEqual(extract_number("صد هزار"), 100000)
        self.assertEqual(extract_number("منفی ۲"), -2)
        self.assertEqual(extract_number("منفی هفتاد"), -70)

        # Verify non-power multiples of ten no longer discard
        # adjacent multipliers
        self.assertEqual(extract_number("بیست هزار"), 20000)
        self.assertEqual(extract_number("پنجاه میلیون"), 50000000)

        # Verify smaller powers of ten no longer cause miscalculation of larger
        # powers of ten (see MycroftAI#86)
        self.assertEqual(extract_number("بیست میلیارد و سیصد میلیون و  \
                                        نهصد و پنجاه هزار و  \
                                        ششصد و هفتاد و پنج و هشت دهم"),
                         20300950675.8)
        self.assertEqual(extract_number("نهصد و نود و نه میلیون و  \
                                        نهصد و نود و نه هزار و  \
                                        نهصد و نود و نه و نه دهم"),
                         999999999.9)

        # TODO why does "trillion" result in xxxx.0?
        self.assertEqual(extract_number("هشصد میلیارد و دویست و پنجاه و هفت"), 
                                        800000000257.0)

        self.assertTrue(extract_number("تنیسور سریع است") is False)
        self.assertTrue(extract_number("شکستنی") is False)

        self.assertTrue(extract_number("صفر شکستنی") is not False)
        self.assertEqual(extract_number("صفر شکستنی"), 0)

        self.assertTrue(extract_number("خشن 0") is not False)
        self.assertEqual(extract_number("خشن 0"), 0)

        self.assertEqual(extract_number("کاملا 100%"), 100)

    def test_extract_duration_fa(self):
        self.assertEqual(extract_duration("10 ثانیه"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5 دقیقه"),
                         (timedelta(minutes=5), ""))
        self.assertEqual(extract_duration("2 ساعت"),
                         (timedelta(hours=2), ""))
        self.assertEqual(extract_duration("3 روز"),
                         (timedelta(days=3), ""))
        self.assertEqual(extract_duration("25 هفته"),
                         (timedelta(weeks=25), ""))
        self.assertEqual(extract_duration("هفت ساعت"),
                         (timedelta(hours=7), ""))
        self.assertEqual(extract_duration("7.5 ثانیه"),
                         (timedelta(seconds=7.5), ""))
        self.assertEqual(extract_duration("هشت و نیم روز و سی و نه ثانیه"),
                         (timedelta(days=8.5, seconds=39), ""))
        self.assertEqual(extract_duration("سه هفته و چهارصد و نود و هفت روز و "
                                          "سیصد و ۹۱.۶ ثانیه در بیدارم کن"),
                         (timedelta(weeks=3, days=497, seconds=391.6),
                          "در بیدارم کن"))
        self.assertEqual(extract_duration("10-ثانیه"),
                         (timedelta(seconds=10.0), ""))
        self.assertEqual(extract_duration("5-دقیقه"),
                         (timedelta(minutes=5), ""))

    def test_extract_duration_case_fa(self):
        self.assertEqual(extract_duration("یک تایمر برای ۳۰ دقیقه تنظیم کن"),
                         (timedelta(minutes=30), "1 تایمر برای تنظیم کن"))
        self.assertEqual(extract_duration("این فیلم یک ساعت و "
                                          "پنجاه و هفت و نیم دقیقه است"),
                         (timedelta(hours=1, minutes=57.5),
                             "این فیلم است"))
        self.assertEqual(extract_duration("چهار و نیم دقیقه تا غروب"),
                         (timedelta(minutes=4.5), "تا غروب"))
        self.assertEqual(extract_duration("نوزده دقیقه از ساعت گذشته"),
                         (timedelta(minutes=19), "از ساعت گذشته"))

    def test_extractdatetime_fractions_fa(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("کمین را برای نیم ساعت تنظیم کن",
                    "2017-06-27 13:34:00", "کمین را تنظیم کن")
        testExtract("در نیم ساعت یادم بنداز به مادرم زنگ بزنم",
                    "2017-06-27 13:34:00", "یادم بنداز به مادرم زنگ بزنم")

    def test_extractdatetime_fa(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 13, 4, tzinfo=default_timezone())  # Tue June 27, 2017 @ 1:04pm
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("الان وقتشه",
                    "2017-06-27 13:04:00", "وقتشه")
        testExtract("یک ثانیه",
                    "2017-06-27 13:04:01", "")
        testExtract("یک دقیقه",
                    "2017-06-27 13:05:00", "")
        testExtract("یک دهه",
                    "2027-06-27 00:00:00", "")
        testExtract("دهه بعد",
                    "2027-06-27 00:00:00", "")
        testExtract("یک قرن",
                    "2117-06-27 00:00:00", "")
        testExtract("یک هزاره",
                    "3017-06-27 00:00:00", "")
        testExtract("یک ساعت",
                    "2017-06-27 14:04:00", "")
        testExtract("من آن را در عرض یک ساعت می خواهم",
                    "2017-06-27 14:04:00", "من آن را می خواهم")
        testExtract("۱ ثانیه",
                    "2017-06-27 13:04:01", "")
        testExtract("کمین را برای یک دقیقه تنظیم کن",
                    "2017-06-27 13:05:00", "کمین را تنظیم کن")
        testExtract("از امروز برای ۵ روز کمین بگذارید",
                    "2017-07-02 00:00:00", "کمین بگذارید")
        testExtract("پسفردا",
                    "2017-06-29 00:00:00", "")
        testExtract("پسفردا هوا چطوره؟",
                    "2017-06-29 00:00:00", "هوا چطوره")
        testExtract("10:45 بعد از ظهر یادم بنداز",
                    "2017-06-27 22:45:00", "یادم بنداز")
        testExtract("جمعه صبح هوا چطوره",
                    "2017-06-30 08:00:00", "هوا چطوره")
        testExtract("فردا هوا چطوره",
                    "2017-06-28 00:00:00", "هوا چطوره")
        testExtract("بعد از ظهر هوا چطوره",
                    "2017-06-27 15:00:00", "هوا چطوره")
        testExtract("عصر هوا چطوره",
                    "2017-06-27 19:00:00", "هوا چطوره")
        testExtract("امروز صبح هوا چطور بود",
                    "2017-06-27 08:00:00", "هوا چطور بود")
        testExtract("بعد از ۸ هفته و دو روز یادم بنداز به مادر زنگ بزنم",
                    "2017-08-24 00:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("سوم اوت یادم بنداز به مادر زنگ بزنم",
                    "2017-08-03 00:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("فردا ساعت ۷ صبح یادم بنداز به مادر زنگ بزنم",
                    "2017-06-28 07:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("فردا ساعت ۱۰ شب یادم بنداز به مادر زنگ بزنم",
                    "2017-06-28 22:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("ساعت ۷ صبح یادم بنداز به مادر زنگ بزنم",
                    "2017-06-28 07:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("بعد یک ساعت یادم بنداز به مادر زنگ بزنم",
                    "2017-06-27 14:04:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("ساعت ۱۷ و ۳۰ یادم بنداز به مادر زنگ بزنم",
                    "2017-06-27 17:30:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("ساعت ۰۶ و ۳۰ یادم بنداز به مادر زنگ بزنم",
                    "2017-06-28 06:30:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("ساعت ۰۶ ۳۰ یادم بنداز به مادر زنگ بزنم",
                    "2017-06-28 06:30:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("پنجشنبه صبح ساعت ۷ یادم بنداز به مادر زنگ بزنم",
                    "2017-06-29 07:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("پنجشنبه عصر ساعت ۷ یادم بنداز به مادر زنگ بزنم",
                    "2017-06-29 19:00:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("بعد ۲ ساعت یادم بنداز به مادر زنگ بزنم",
                    "2017-06-27 15:04:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("۲ ساعت دیگه یادم بنداز به مادر زنگ بزنم",
                    "2017-06-27 15:04:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("پانزده دقیقه دیگه یادم بنداز به مادر زنگ بزنم",
                    "2017-06-27 13:19:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("بعد پانزده دقیقه یادم بنداز به مادر زنگ بزنم",
                    "2017-06-27 13:19:00", "یادم بنداز به مادر زنگ بزنم")
        testExtract("پنجشنبه ساعت ۳:۴۵ بعد از ظهر حمله رو شروع کنید",
                    "2017-06-29 15:45:00", "حمله رو شروع کنید")
        testExtract("دوشنبه از نانوایی نان سفارش بده",
                    "2017-07-03 00:00:00", "از نانوایی نان سفارش بده")
        testExtract("پنجشنبه بعد ساعت ۱۲:۴۵ به مامان زنگ بزن",
                    "2017-07-06 12:45:00", "به مامان زنگ بزن")
        testExtract("جمعه بعد هوا چطوره؟",
                    "2017-06-30 00:00:00", "هوا چطوره")
        testExtract("چهارشنبه بعد هوا چطوره؟",
                    "2017-07-05 00:00:00", "هوا چطوره")
        testExtract("جمعه بعد صبح هوا چطوره؟",
                    "2017-06-30 08:00:00", "هوا چطوره")
        testExtract("جمعه بعد عصر هوا چطوره؟",
                    "2017-06-30 19:00:00", "هوا چطوره")
        testExtract("جمعه بعد بعد از ظهر هوا چطوره",
                    "2017-06-30 15:00:00", "هوا چطوره")
        testExtract("۴ام جولای آتش بازی بخر",
                    "2017-07-04 00:00:00", "آتش بازی بخر")
        testExtract("۴ام ژوئیه آتش بازی بخر",
                    "2017-07-04 00:00:00", "آتش بازی بخر")
        testExtract("این پنجشنبه هوا چطوره",
                    "2017-06-29 00:00:00", "هوا چطوره")
        testExtract("پنجشنبه ساعت ۸ بعد از ظهر حمله رو شروع کنید",
                    "2017-06-29 20:00:00", "حمله رو شروع کنید")
        testExtract("ظهر پنجشنبه حمله رو شروع کنید",
                    "2017-06-29 12:00:00", "حمله رو شروع کنید")
        testExtract("نصف شب پنجشنبه حمله رو شروع کنید",
                    "2017-06-29 00:00:00", "حمله رو شروع کنید")
        testExtract("۴ سال بعد یادم بنداز بیدار شم",
                    "2021-06-27 00:00:00", "یادم بنداز بیدار شم")
        testExtract("۴ سال و ۴ روز بعد یادم بنداز بیدار شم",
                    "2021-07-01 00:00:00", "یادم بنداز بیدار شم")
        testExtract("۳ دسامبر",
                    "2017-12-03 00:00:00", "")
        testExtract("امشب ساعت ۸:۰۰ ملاقات کنیم",
                    "2017-06-27 20:00:00", "ملاقات کنیم")
        testExtract("۵ عصر ملاقات کنیم",
                    "2017-06-27 17:00:00", "ملاقات کنیم")
        testExtract("۸ صبح ملاقات کنیم",
                    "2017-06-28 08:00:00", "ملاقات کنیم")
        testExtract("ساعت ۸ صبح بیدارم کن",
                    "2017-06-28 08:00:00", "بیدارم کن")
        testExtract("پنجشنبه هوا چطوره",
                    "2017-06-29 00:00:00", "هوا چطوره")
        testExtract("دوشنبه هوا چطوره",
                    "2017-07-03 00:00:00", "هوا چطوره")
        testExtract("این چهارشنبه هوا چطوره",
                    "2017-06-28 00:00:00", "هوا چطوره")
        testExtract("دوشنبه قبل هوا چطور بود",
                    "2017-06-26 00:00:00", "هوا چطور بود")
        testExtract("برای چهارشنبه ساعت ۸ عصر هشدار تنظیم کن",
                    "2017-06-28 20:00:00", "هشدار تنظیم کن")
        testExtract("عصر پنجم ژوئن 2017 یادم بنداز به مامان زنگ بزنم",
                    "2017-06-05 19:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("بعد ۳ هفته یادم بنداز به مامان زنگ بزنم",
                    "2017-07-18 00:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("بعد ۸ هفته و دو روز یادم بنداز به مامان زنگ بزنم",
                    "2017-08-24 00:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("بعد ۴ روز یادم بنداز به مامان زنگ بزنم",
                    "2017-07-01 00:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("بعد ۳ ماه یادم بنداز به مامان زنگ بزنم",
                    "2017-09-27 00:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("بعد ۲ سال و دو روز یادم بنداز به مامان زنگ بزنم",
                    "2019-06-29 00:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("هفته بعد یادم بنداز به مامان زنگ بزنم",
                    "2017-07-04 00:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("شنبه ۱۰ صبح یادم بنداز به مامان زنگ بزنم",
                    "2017-07-01 10:00:00", "یادم بنداز به مامان زنگ بزنم")
        testExtract("شنبه بعد ساعت ۱۰ صبح یادم بنداز به مامان زنگ بزنم",
                    "2017-07-01 10:00:00", "یادم بنداز به مامان زنگ بزنم")

        # test yesterday
        testExtract("دیروز چه روزی بود",
                    "2017-06-26 00:00:00", "چه روزی بود")
        testExtract("دیروز ساعت ۶ شام خوردم",
                    "2017-06-26 06:00:00", "شام خوردم")
        testExtract("دیروز ساعت ۶ صبح شام خوردم",
                    "2017-06-26 06:00:00", "شام خوردم")
        testExtract("دیروز ساعت ۶ عصر شام خوردم",
                    "2017-06-26 18:00:00", "شام خوردم")

        testExtract("امشب ۸",
                    "2017-06-27 20:00:00", "")
        testExtract("امشب ۸:۳۰",
                    "2017-06-27 20:30:00", "")
        # Tests a time with ':' & without am/pm
        testExtract("برای امشب ۹:۳۰ هشدار تنظیم کن",
                    "2017-06-27 21:30:00", "هشدار تنظیم کن")
        testExtract("برای امشب ۹:۰۰ هشدار تنظیم کن",
                    "2017-06-27 21:00:00", "هشدار تنظیم کن")

        #  "# days ago>"
        testExtract("تولدم ۱ روز پیش بود",
                    "2017-06-26 00:00:00", "تولدم بود")
        testExtract("تولدم ۲ روز پیش بود",
                    "2017-06-25 00:00:00", "تولدم بود")

    def test_extract_ambiguous_time_fa(self):
        morning = datetime(2017, 6, 27, 8, 1, 2, tzinfo=default_timezone())
        evening = datetime(2017, 6, 27, 20, 1, 2, tzinfo=default_timezone())
        noonish = datetime(2017, 6, 27, 12, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('به ماهی غذا بده'), None)
        self.assertEqual(
            extract_datetime('روز'), None)
        self.assertEqual(
            extract_datetime('هفته'), None)
        self.assertEqual(
            extract_datetime('ماه'), None)
        self.assertEqual(
            extract_datetime('سال'), None)
        self.assertEqual(
            extract_datetime(' '), None)

    def test_extract_relativedatetime_fa(self):
        def extractWithFormat(text):
            date = datetime(2017, 6, 27, 10, 1, 2, tzinfo=default_timezone())
            [extractedDate, leftover] = extract_datetime(text, date)
            extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
            return [extractedDate, leftover]

        def testExtract(text, expected_date, expected_leftover):
            res = extractWithFormat(normalize(text))
            self.assertEqual(res[0], expected_date, "for=" + text)
            self.assertEqual(res[1], expected_leftover, "for=" + text)

        testExtract("۵ دقیقه بعد ملاقات کنیم",
                    "2017-06-27 10:06:02", "ملاقات کنیم")
        testExtract("۵دقیقه بعد ملاقات کنیم",
                    "2017-06-27 10:06:02", "ملاقات کنیم")
        testExtract("۵ ثانیه بعد ملاقات کنیم",
                    "2017-06-27 10:01:07", "ملاقات کنیم")
        testExtract("یک ساعت بعد ملاقات کنیم",
                    "2017-06-27 11:01:02", "ملاقات کنیم")
        testExtract("۲ساعت بعد ملاقات کنیم",
                    "2017-06-27 12:01:02", "ملاقات کنیم")
        testExtract("۵ثانیه بعد ملاقات کنیم",
                    "2017-06-27 10:01:07", "ملاقات کنیم")

    def test_normalize_numbers(self):
        self.assertEqual(normalize("ساعت دو به دو یادم بنداز"),
                         "ساعت 2 به 2 یادم بنداز")
        self.assertEqual(normalize('دو دقیقه بعد ساعت چند میشه'),
                         '2 دقیقه بعد ساعت چند میشه')
        self.assertEqual(normalize('بیست و دو دقیقه بعد ساعت چند میشه'),
                         '22 دقیقه بعد ساعت چند میشه')
        self.assertEqual(normalize("بیست به دو یادم بنداز"),
                         "20 به 2 یادم بنداز")

        # test ordinals
        self.assertEqual(normalize('این اولیه'),
                         'این اول')
        self.assertEqual(normalize('این اول دومیه'),
                         'این یکم دوم')

    def test_extract_date_with_number_words(self):
        now = datetime(2019, 7, 4, 8, 1, 2, tzinfo=default_timezone())
        self.assertEqual(
            extract_datetime('۲ دقیقه بعد ساعت چند میشه', now)[0],
            datetime(2019, 7, 4, 8, 3, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('دو دقیقه بعد ساعت چند میشه', now)[0],
            datetime(2019, 7, 4, 8, 3, 2, tzinfo=default_timezone()))
        self.assertEqual(
            extract_datetime('دویست دقیقه بعد چی میشه', now)[0],
            datetime(2019, 7, 4, 11, 21, 2, tzinfo=default_timezone()))

    def test_numbers(self):
        self.assertEqual(normalize("این تست یک دو سه است"),
                         "این تست 1 2 3 است")
        self.assertEqual(normalize("  این تست چهار پنج شش است"),
                         "این تست 4 5 6 است")
        self.assertEqual(normalize("این تست هفت هشت نه است"),
                         "این تست 7 8 9 است")
        self.assertEqual(normalize("این تست ده یازده دوازده است"),
                         "این تست 10 11 12 است")
        self.assertEqual(normalize("این تست سیزده چهارده است"),
                         "این تست 13 14 است")
        self.assertEqual(normalize("این پانزده شانزده هفده است"),
                         "این 15 16 17 است")
        self.assertEqual(normalize("این هجده نوزده بیست است"),
                         "این 18 19 20 است")
        self.assertEqual(normalize("این یک نوزده بیست و دو است"),
                         "این 1 19 22 است")
        self.assertEqual(normalize("این صد است"),
                         "این 100 است")
        self.assertEqual(normalize("این یک دو بیست و دو است"),
                         "این 1 2 22 است")
        self.assertEqual(normalize("این یک و نیم است"),
                         "این 1.5 است")
        self.assertEqual(normalize("این یک و نیم و پنج و شش است"),
                         "این 1.5 5 6 است")

    def test_multiple_numbers(self):
        self.assertEqual(extract_numbers("این تست یک دو سه است"),
                         [1.0, 2.0, 3.0])
        self.assertEqual(extract_numbers("این تست چهار پنج شش است"),
                         [4.0, 5.0, 6.0])
        self.assertEqual(extract_numbers("این تست ده یازده دوازده است"),
                         [10.0, 11.0, 12.0])
        self.assertEqual(extract_numbers("این تست یک بیست و یک است"),
                         [1.0, 21.0])
        self.assertEqual(extract_numbers("۱ سگ، هفت خوک، مک دونالد مزرعه دارد "
                                         "۳ ضرب در ۵"),
                         [1.0, 7.0, 3.0, 5.0])
        self.assertEqual(extract_numbers("دو آبجو برای دو خرس"),
                         [2.0, 2.0])
        self.assertEqual(extract_numbers("بیست ۲۰ بیست"),
                         [20, 20, 20])
        self.assertEqual(extract_numbers("بیست ۲۰ ۲۲"),
                         [20.0, 20.0, 22.0])
        self.assertEqual(extract_numbers("بیست بیست و دو بیست"),
                         [20, 22, 20])
        self.assertEqual(extract_numbers("بیست و ۲"),
                         [22.0])
        self.assertEqual(extract_numbers("بیست ۲۰ بیست و ۲"),
                         [20, 20, 22])
        self.assertEqual(extract_numbers("یک سوم یک"),
                         [1 / 3, 1])
        self.assertEqual(extract_numbers("سومی", ordinals=True), [3])
        self.assertEqual(extract_numbers("شش تریلیون", short_scale=True),
                         [6e12])
        self.assertEqual(extract_numbers("شش تریلیون", short_scale=False),
                         [6e12])
        self.assertEqual(extract_numbers("دو خوک و شش تریلیون باکتری",
                                         short_scale=True), [2, 6e12])
        self.assertEqual(extract_numbers("دو خوک و شش تریلیون باکتری",
                                         short_scale=False), [2, 6e12])
        self.assertEqual(extract_numbers("سی و دوم یا یک",
                                         ordinals=True), [32.0])
        self.assertEqual(extract_numbers("این تست هفت هشت نه و نیم است"),
                         [7.0, 8.0, 9.5])

    # def test_contractions(self):
    #     pass

if __name__ == "__main__":
    unittest.main()
