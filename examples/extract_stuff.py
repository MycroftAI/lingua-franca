from lingua_franca.parse import extract_datetime, extract_number, \
    extract_numbers, extract_duration, normalize

# extract a number
assert extract_number("nothing") is False
assert extract_number("two million five hundred thousand tons of spinning "
                      "metal") == 2500000
assert extract_number("six trillion") == 6000000000000.0
assert extract_number("six trillion", short_scale=False) == 6e+18

assert extract_number("1 and 3/4 cups") == 1.75
assert extract_number("1 cup and a half") == 1.5

## extracts all numbers
assert extract_numbers("nothing") == []
assert extract_numbers("this is a one twenty one  test") == [1.0, 21.0]
assert extract_numbers("1 dog, seven pigs, macdonald had a farm, "
                       "3 times 5 macarena") == [1, 7, 3, 5]

## extract durations
from datetime import timedelta

assert extract_duration("nothing") == (None, 'nothing')

assert extract_duration("Nineteen minutes past the hour") == (
    timedelta(minutes=19),
    "past the hour")
assert extract_duration("wake me up in three weeks, four hundred ninety seven"
                        " days, and three hundred 91.6 seconds") == (
           timedelta(weeks=3, days=497, seconds=391.6),
           "wake me up in , , and")
assert extract_duration(
    "The movie is one hour, fifty seven and a half minutes long") == (
           timedelta(hours=1, minutes=57.5),
           "the movie is ,  long")

## extract date times
from datetime import datetime


def extractWithFormat(text):
    date = datetime(2017, 6, 27, 13, 4)  # Tue June 27, 2017 @ 1:04pm
    [extractedDate, leftover] = extract_datetime(text, date)
    extractedDate = extractedDate.strftime("%Y-%m-%d %H:%M:%S")
    return [extractedDate, leftover]


def testExtract(text, expected_date, expected_leftover):
    res = extractWithFormat(normalize(text))
    assert res[0] == expected_date
    assert res[1] == expected_leftover


testExtract("now is the time",
            "2017-06-27 13:04:00", "is time")
testExtract("in a couple minutes",
            "2017-06-27 13:06:00", "")
testExtract("What is the day after tomorrow's weather?",
            "2017-06-29 00:00:00", "what is weather")
testExtract("Remind me at 10:45 pm",
            "2017-06-27 22:45:00", "remind me")
testExtract("what is the weather on friday morning",
            "2017-06-30 08:00:00", "what is weather")
testExtract("what is tomorrow's weather",
            "2017-06-28 00:00:00", "what is weather")
testExtract("remind me to call mom next tuesday",
            "2017-07-04 00:00:00", "remind me to call mom")
testExtract("remind me to call mom in 3 weeks",
            "2017-07-18 00:00:00", "remind me to call mom")
testExtract("set an alarm for tonight 9:30",
            "2017-06-27 21:30:00", "set alarm")
testExtract("on the evening of june 5th 2017 remind me to call my mother",
            "2017-06-05 19:00:00", "remind me to call my mother")
