from lingua_franca.format import nice_duration, nice_date, nice_date_time, \
    nice_number, nice_time, pronounce_number

# pronounce numbers
assert nice_number(25/6) == "4 and a sixth"
assert nice_number(201) == "201"
assert nice_number(3.14159269) == "3 and a seventh"

assert pronounce_number(3.14159269) == "three point one four"
assert pronounce_number(0) == "zero"
assert pronounce_number(10) == "ten"
assert pronounce_number(201) == "two hundred and one"
assert pronounce_number(102.3) == "one hundred and two point three"
assert pronounce_number(
    4092949192) == "four billion, ninety two million, nine hundred and forty nine thousand, one hundred and ninety two"

assert pronounce_number(100034000000299792458, short_scale=True) == \
       "one hundred quintillion, thirty four quadrillion, " \
       "two hundred and ninety nine million, seven hundred and ninety " \
       "two thousand, four hundred and fifty eight"

assert pronounce_number(100034000000299792458, short_scale=False) == \
       "one hundred trillion, thirty four thousand billion, " \
       "two hundred and ninety nine million, seven hundred and ninety " \
       "two thousand, four hundred and fifty eight"

# pronounce datetime objects
import datetime

dt = datetime.datetime(2017, 1, 31,  13, 22, 3)

assert nice_date(dt) == "tuesday, january thirty-first, twenty seventeen"

assert nice_time(dt) == "one twenty two"
assert nice_time(dt, use_ampm=True) ==  "one twenty two p.m."
assert nice_time(dt, speech=False) == "1:22"
assert nice_time(dt, speech=False, use_ampm=True) == "1:22 PM"
assert nice_time(dt, speech=False, use_24hour=True) == "13:22"
assert nice_time(dt, speech=False, use_24hour=True, use_ampm=True) == "13:22"
assert nice_time(dt, use_24hour=True, use_ampm=True) == "thirteen twenty two"
assert nice_time(dt, use_24hour=True, use_ampm=False) == "thirteen twenty two"

assert nice_date_time(dt) == "tuesday, january thirty-first, twenty seventeen at one twenty two"

# pronounce durations
assert nice_duration(1) ==   "one second"
assert nice_duration(3) ==   "three seconds"
assert nice_duration(1, speech=False) ==   "0:01"
assert nice_duration(61), "one minute one second"
assert nice_duration(61, speech=False) ==   "1:01"
assert nice_duration(5000) ==  "one hour twenty three minutes twenty seconds"
assert nice_duration(5000, speech=False), "1:23:20"
assert nice_duration(50000) ==   "thirteen hours fifty three minutes twenty seconds"
assert nice_duration(50000, speech=False) ==   "13:53:20"
assert nice_duration(500000) ==   "five days  eighteen hours fifty three minutes twenty seconds"
assert nice_duration(500000, speech=False), "5d 18:53:20"
assert nice_duration(datetime.timedelta(seconds=500000), speech=False) ==  "5d 18:53:20"