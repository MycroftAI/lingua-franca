# Project Structure and Notes

## Source code layout

    * user-facing functions live here
    
    lingua_franca/
    ├─ __init__.py * (exposes certain internal functions)
    ├─ format.py *
    ├─ internal.py
    ├─ time.py *
    ├─ parse.py *
    ├─ lang/ (localized functions and basic language data)
    │  ├─ common_data_<>.py (data structures related to language '<>')
    │  ├─ format_<>.py (localized formatters)
    │  ├─ parse_<>.py (localized parsers)
    ├─ res/ (fully localized data, 'en-us' vs 'en-au' and etc.)
    │  ├─ text/
    │  │  ├─ <lang-code>/
    │  │  │  ├─ date_time.json
    │  │  │  ├─ common words

----

## Adding new languages

Ensure that all supported languages are registered in `lingua_franca.internal.py`, in the list
`_SUPPORTED_LANGUAGES`.

## Localizing functions

If you are localizing an existing top-level function, there is no need to alter the top-level
module to which your function belongs. Lingua Franca will discover all localized versions
of its top-level functions.

Localized functions live in `lingua_franca/lang/`, in files named for their corresponding module.

>For example, the top level formatting module is `lingua_franca.format`, and lives at
`lingua_franca/format.py`.

>English formatters live in `lingua_franca/lang/format_en.py`.  
>Spanish formatters live in `lingua_franca/lang/format_es.py`.  
>Spanish *parsers*, corresponding to
`lingua_franca.parse` and `lingua_franca/parse.py`,  
>live in `lingua_franca/lang/parse_es.py`.

Note that these use a *primary* language code, such as `en` or `es`, rather than a *full* language
code, such as `en-US` or `es-ES`. Details relating to regional dialects reside in `res`.

Lingua Franca will find your function by itself, as long as

- Your files are named properly
- Your function and its signature are named and organized properly (described below) and
- Your primary language code is registered as a supported language with Lingua Franca itself, in
`lingua_franca.internal._SUPPORTED_LANGUAGES`

What you must do:

- Implement the function with its uniform name, using the appropriate language code.
  - `lingua_franca.lang.format_en.pronounce_number_en`
  - `lingua_franca.lang.format_es.pronounce_number_es`
  - `lingua_franca.lang.format_pt.pronounce_number_pt`
- Name function arguments exactly as they are named in the top-level modules
  - You do not need to implement all arguments, but you must name them identically
  - All arguments must be keyword arguments (except the primary arguments)
  - If you need to add new arguments,
        feel free, but MAKE SURE you add the argument to the top-level function, as a keyword arg.
        This is the only time you should need to modify the top-level functions while localizing.
        Ensure that any new arguments are at the end of the function signatures, both in the
        top-level function, and in your localized function.

## Adding new functions

Ensure that all functions which will have localized versions are registered in their module's
`_REGISTERED_FUNCTIONS` tuple, conventionally defined near the top.

For example, formatters which have been or will be localized are registered in
  `lingua_franca.format._REGISTERED_FUNCTIONS`, by name only.

As of July, 2020, this tuple looks as follows:

  ```python3
  # lingua_franca/format.py

  _REGISTERED_FUNCTIONS = ("nice_number",
                         "nice_time",
                         "pronounce_number",
                         "nice_response")
  ```

All top-level functions which have localized versions are wrapped using
`lingua_franca.internal.localized_function`, like so:

    @localized_function
    def foo(bar, baz):
        pass

Note that this function is a pass-through, and would not be executed even if it
had logic of its own. The wrapper can fall back on the wrapped function if it is
passed an error or errors as triggers:

    @localized_function(run_own_code_on=[ValueError, IndexError])
    def func(bar, baz):
        print("Something happened!")

In the above example, calling `func(x, y)` will usually find and call a localized
version of `func`. However, if during that process something raises a
`ValueError` or `IndexError`, then (and only then) it will execute `func` itself,
and print "Something happened!"