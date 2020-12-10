[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE.md) [![CLA](https://img.shields.io/badge/CLA%3F-Required-blue.svg)](https://mycroft.ai/cla) [![Team](https://img.shields.io/badge/Team-Languages-violetblue.svg)](https://github.com/MycroftAI/contributors/blob/master/team/Languages.md) ![Status](https://img.shields.io/badge/-Alpha-orange.svg)

[![Build Status](https://travis-ci.org/MycroftAI/lingua-franca.svg?branch=master)](https://travis-ci.org/MycroftAI/lingua-franca) [![Coverage Status](https://coveralls.io/repos/github/MycroftAI/lingua-franca/badge.svg?branch=master)](https://coveralls.io/github/MycroftAI/lingua-franca?branch=master)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Join chat](https://img.shields.io/badge/Mattermost-join_chat-brightgreen.svg)](https://chat.mycroft.ai/community/channels/languages)

# Lingua Franca

Mycroft's multilingual text parsing and formatting library

Lingua Franca (_noun_)<br>
> a framework that is adopted as the common language between speakers with different native tongues</dr>


- [Lingua Franca](#lingua-franca)
  - [Formatting](#formatting)
    - [Pronounce numbers](#pronounce-numbers)
    - [Pronounce datetime objects](#pronounce-datetime-objects)
    - [Pronounce durations](#pronounce-durations)
  - [Parsing](#parsing)
    - [Extract numbers](#extract-numbers)
    - [Extract durations](#extract-durations)
    - [Extract dates](#extract-dates)
  - [Contributing to this project](#contributing-to-this-project)
    - [0. Sign a Contributor Licensing Agreement](#0-sign-a-contributor-licensing-agreement)
    - [1. Setup a local copy of the project](#1-setup-a-local-copy-of-the-project)
    - [2. Writing tests](#2-writing-tests)
    - [3. Run tests to confirm they fail](#3-run-tests-to-confirm-they-fail)
    - [4. Write code](#4-write-code)
    - [5. Document your code](#5-document-your-code)
    - [6. Try it in Mycroft](#6-try-it-in-mycroft)
    - [7. Commit changes](#7-commit-changes)
    - [8. Submit a PR](#8-submit-a-pr)
    - [9. Waiting for a review](#9-waiting-for-a-review)
  - [Credits](#credits)

## Formatting

Convert data into spoken equivalents

### Pronounce numbers

spoken versions of numbers

```python
from lingua_franca.format import nice_number, pronounce_number

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
```

### Pronounce datetime objects

spoken date for datetime.datetime objects

```python
from lingua_franca.format import nice_date, nice_date_time, nice_time
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
```

### Pronounce durations

spoken number of seconds or datetime.timedelta objects

```python
from lingua_franca.format import nice_duration


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

from datetime import timedelta

assert nice_duration(timedelta(seconds=500000), speech=False) ==  "5d 18:53:20"
```

## Parsing

Extract data from natural language text

### Extract numbers

```python
from lingua_franca.parse import extract_number, extract_numbers

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
```

### Extract durations

extract datetime.timedelta objects

```python
## extract durations
from lingua_franca.parse import extract_duration
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
```

### Extract dates

extract datetime.datetime objects

```python
## extract date times
from datetime import datetime
from lingua_franca.parse import extract_datetime, normalize

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

```

## Getting Started

### Loading a language

Before using Lingua Franca's other functions, you'll need to load one or more languages into memory, using part or all of a
BCP-47 language code:

```python
# Load a language
lingua_franca.load_language('en')

# Load multiple languages at once
#
# If no default language is set, the first
# element will become the default
lingua_franca.load_languages(['en', 'es'])

# Change the default language
lingua_franca.set_default_language('es')
```

See the documentation for more information about loading and unloading languages.

### Calling localized functions

Most of Lingua Franca's functions have been localized. You can call a function in any language you've loaded; this is always specified by the function's `lang` parameter. If you omit that parameter, the function will be called in the current default language.

Example:

```python
>>> from lingua_franca import load_languages, \
  set_default_lang, parse
>>> load_languages(['es', 'en'])
>>> parse.extract_number("uno")
1
>>> parse.extract_number("one")
False
>>> parse.extract_number("one", lang='en')
1
>>> set_default_lang('en')
>>> parse.extract_number("uno")
False
>>> parse.extract_number("one")
1
```

In some languages, certain parameters have no effect, either because
those parameters do not apply, or because the localization is not complete.

It's important to remember that Lingua Franca is in alpha. Support for a
particular language may be inconsistent, and one language's version of a
complex function might be outdated compared with another.

New functionality usually starts in the languages spoken by major
contributors. If your language's functions are lacking, we'd love your help
improving them! (See below, "Contributing.")

## Contributing to this project

We welcome all contributions to Lingua Franca. To get started:

### 0. Sign a Contributor Licensing Agreement

To protect yourself, the project, and users of Mycroft technologies, we require a Contributor Licensing Agreement (CLA) before accepting any code contribution. This agreement makes it crystal clear that, along with your code, you are offering a license to use it within the confines of this project. You retain ownership of the code, this is just a license.

You will also be added to [our list of excellent human beings](https://github.com/MycroftAI/contributors)!

Please visit https://mycroft.ai/cla to initiate this one-time signing.

### 1. Setup a local copy of the project

1. [Fork the project](https://help.github.com/articles/fork-a-repo/) to create your own copy.

2. Clone the repository and change into that directory

```bash
git clone https://github.com/your-username/lingua-franca/
cd lingua-franca
```

3. Setup a lightweight virtual environment (venv) for the project. This creates an isolated environment that can have it's own independent set of installed Python packages.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

  To exit the venv you can run `deactivate` or close the terminal window.

4. Install the package and it's dependencies

```bash
pip install wheel
python -m pip install .
pip install pytest
python setup.py install
```

5. To check that everything is installed correctly, let's run the existing test-suite.

```bash
pytest
```

### 2. Have a look at the project's structure

The package's layout is described in `project-structure.md`, along with some important notes. It's pretty
intuitive, but uniform file and function names are important to Lingua Franca's operation.

### 3. Writing tests

We utilize a Test Driven Development (TDD) methodology so the first step is always to add tests for whatever you want to add or fix. If it's a bug, we must not have a test that covers that specific case, so we want to add another test. If you are starting on a new language then you can take a look at the tests for other languages to get started.

Tests are all located in `lingua_franca/test`.
Each language should have two test files:

- `test_format_lang.py`
- `test_parse_lang.py`

### 4. Run tests to confirm they fail

Generally, using TDD, all tests should fail when they are first added. If the test is passing when you haven't yet fixed the bug or added the functionality, something must be wrong with the test or the test runner.

```bash
pytest
```

### 5. Write code

Now we can add our new code. There are three main files for each language:

- `common_data_lang.py`  
  Common data that can be used across formatting and parsing such as dictionaries of number names.
- `format_lang.py`  
  All formatting functions for this language.
- `parse_lang.py`  
  All parsing functions for this language.

Since we have already written our unit tests, we can run these regularly to see our progress.

### 6. Document your code

Document code using [Google-style docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html). Our automated documentation tools expect that format. All functions and class methods that are expected to be called externally should include a docstring. (And those that aren't should be [prefixed with a single underscore](https://docs.python.org/3/tutorial/classes.html#private-variables).

### 7. Try it in Mycroft

Lingua Franca is installed by default when you install Mycroft-core, but for development you generally have this repo cloned elsewhere on your computer. You can use your changes in Mycroft by installing it in the Mycroft virtual environment.

If you added the Mycroft helper commands during setup you can just use:

```bash
mycroft-pip install /path/to/your/lingua-franca
```

Otherwise you need to activate that venv manually:

```bash
cd ~/mycroft-core
source venv-activate.sh
pip install /path/to/your/lingua-franca
```

Now, when talking with Mycroft, it will be using your development version of Lingua Franca.

### 8. Commit changes

Make commits in logical units, and describe them thoroughly. If addressing documented issue, use the issue identifier at the very beginning of each commit. For instance:

```bash
git commit -m "Issues-123 - Fix 'demain' date extraction in French"
```

### 9. Submit a PR

Once your changes are ready for review, [create a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

Like commit messages, the PR title and description should properly describe the changes you have made, along with any additional information that reviewers who do not speak your language might need to understand.

### 10. Waiting for a review

While you wait for a review of your contribution, why not take a moment to review some other pull requests? This is a great way to learn and help progress the queue of pull requests, which means your contribution will be seen more quickly!

## Credits

Though it is now a standalone package, Lingua Franca's codebase was a spinoff from Mycroft-core. In addition to those represented in Lingua Franca's git log, a great many people contributed to this code before the spinoff.  

Although all are listed in MycroftAI's [List of Excellent People](https://github.com/MycroftAI/contributors), it seems proper to acknowledge the specific individuals who helped write *this* package, since they are no longer represented in `git log`.  

To the best of the maintainers' knowledge, all of the "lost" contributors are listed in `pre-spinoff-credits.md`. Names are listed as they appeared in `git log`, or as they are known to the Mycroft community.  

Those who've contributed since the spinoff are, of course, in Lingua Franca's `git log` and the GitHub "Contributors" pane. All contributors are on the List of Excellent People, regardless of when they contributed.  

If you contributed to the original code, and your name is missing from `pre-spinoff-credits.md`, please inform a maintainer or file an issue, so we can give credit where credit is due!