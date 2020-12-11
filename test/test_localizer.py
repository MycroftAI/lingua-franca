import unittest

from sys import version

import lingua_franca
import lingua_franca.parse
import lingua_franca.format

from lingua_franca.internal import localized_function, _SUPPORTED_LANGUAGES


def unload_all_languages():
    """ These tests call this function a LOT. That's as opposed to forcing
        your test util to run them in order. Sadly, spamming this function
        is easier and probably less onerous for most devs.
    """
    lingua_franca._set_active_langs([])


def setUpModule():
    unload_all_languages()


def tearDownModule():
    unload_all_languages()


class TestException(unittest.TestCase):
    def setUpClass():
        unload_all_languages()

    def tearDownClass():
        unload_all_languages()

    def test_must_load_language(self):
        unload_all_languages()
        self.assertRaises(ModuleNotFoundError,
                          lingua_franca.parse.extract_number, 'one')

    def test_run_own_code_on(self):
        lingua_franca.load_language('en')
        # nice_number() has a run_own_code_on for unrecognized languages,
        # because backwards compatibility requires it to fall back on
        # str(input_value) rather than failing loudly
        #
        # 'cz' is not a supported language, so the function will raise
        # an UnsupportedLanguageError, but nice_number() is decorated with
        # @localized_function(run_own_code_on=[UnsupportedLanguageError])
        self.assertEqual(lingua_franca.format.nice_number(123, lang='cz'),
                         "123")
        self.assertEqual(lingua_franca.format.nice_number(123.45, speech=False, lang='cz'),
                         "123.45")
        # It won't intercept other exceptions, though!
        with self.assertRaises(ModuleNotFoundError):
            unload_all_languages()
            lingua_franca.format.nice_number(123.45)
            # ModuleNotFoundError: No language module loaded.

        with self.assertRaises(ValueError):
            @localized_function("not an error type")
            def foo_must_fail():
                pass
        with self.assertRaises(ValueError):
            @localized_function(print)
            def bar_must_fail_too():
                pass
        with self.assertRaises(ValueError):
            @localized_function([1, 2, 3])
            def baz_must_fail_as_well():
                pass

    def test_type_error(self):
        with self.assertRaises(TypeError):
            lingua_franca.load_language(12)


class TestDeprecation(unittest.TestCase):
    def test_deprecate_explicit_null_lang(self):
        unload_all_languages()
        lingua_franca.set_default_lang('en')
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(
                lingua_franca.parse.extract_number("one", lang=None),
                1
            )
        unload_all_languages()

    def test_deprecate_positional_null_lang(self):
        unload_all_languages()
        lingua_franca.set_default_lang('en')
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(
                lingua_franca.parse.extract_number("one", True, False, None),
                1
            )
        unload_all_languages()


class TestLanguageLoading(unittest.TestCase):

    def test_load_on_demand(self):
        unload_all_languages()
        lingua_franca.load_language("en")
        lingua_franca.config.load_langs_on_demand = True
        self.assertEqual(lingua_franca.parse.extract_number("one", lang="en"),
                         1)
        self.assertEqual(lingua_franca.parse.extract_number("uno", lang="es"),
                         1)

        lingua_franca.config.load_langs_on_demand = False
        # English should still be loaded, but not Spanish
        self.assertEqual(lingua_franca.parse.extract_number("one", lang="en"),
                         1)
        with self.assertRaises(ModuleNotFoundError):
            lingua_franca.parse.extract_number("uno", lang="es")
        unload_all_languages()

    def test_load_language(self):
        lingua_franca.load_language('en')

        # Verify that English is loaded and, since it's the only language
        # we've loaded, also the default.
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        # Verify that English's default full code is 'en-us'
        self.assertEqual(lingua_franca.get_full_lang_code('en'), 'en-us')
        # Verify that this is also our current full code
        self.assertEqual(lingua_franca.get_default_loc(), 'en-us')
        self.assertFalse('es' in lingua_franca.get_active_langs())

        # Verify that unloaded languages can't be invoked explicitly
        self.assertRaises(ModuleNotFoundError,
                          lingua_franca.parse.extract_number,
                          'uno', lang='es')
        unload_all_languages()

    def test_auto_default_language(self):
        lingua_franca.load_language('en')

        # Load two languages, ensure first is default
        lingua_franca.load_languages(['en', 'es'])
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        self.assertEqual(lingua_franca.parse.extract_number('one'), 1)
        unload_all_languages()

    def test_set_default_language(self):
        lingua_franca.load_languages(['es', 'en'])
        lingua_franca.set_default_lang('en')
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        unload_all_languages()

        with self.assertRaises(ValueError):
            lingua_franca.set_default_lang('foobar')

    def test_default_language_singles(self):

        # Load languages one at a time, ensure first is default
        self.assertEqual(lingua_franca.get_active_langs(), [])
        lingua_franca.load_language('en')
        self.assertEqual(lingua_franca.get_default_lang(), 'en')
        lingua_franca.load_language('es')
        self.assertEqual(lingua_franca.get_default_lang(), 'en')

        self.assertEqual(lingua_franca.parse.extract_number('dos'), False)
        self.assertEqual(lingua_franca.parse.extract_number('dos',
                                                            lang='es'),
                         2)

        # Verify default language failover
        lingua_franca.unload_language('en')
        self.assertEqual(lingua_franca.get_default_lang(), 'es')
        unload_all_languages()

    def test_set_active_langs(self):
        unload_all_languages()
        lingua_franca.load_languages(['en', 'es'])
        self.assertEqual(lingua_franca.get_active_langs(),
                         ['en', 'es'])
        lingua_franca._set_active_langs('es')
        self.assertEqual(lingua_franca.get_default_lang(), 'es')
        self.assertFalse('en' in lingua_franca.get_active_langs())
        unload_all_languages()
        with self.assertRaises(TypeError):
            lingua_franca._set_active_langs(157.75)


class TestLocalizerEdgeCases(unittest.TestCase):
    def test_pass_lang_code_positionally(self):
        lingua_franca.load_languages(['en', 'es'])

        self.assertEqual(
            lingua_franca.parse.extract_number("dos", True, False, 'es'),
            2)
        unload_all_languages()

    def test_function_not_localized_error(self):
        lingua_franca.load_language('en')
        with self.assertRaises(
                lingua_franca.internal.FunctionNotLocalizedError):
            lingua_franca.parse.is_ordinal("twelve")
        unload_all_languages()


class TestGetter(unittest.TestCase):
    def test_primary_lang_code(self):
        unload_all_languages()
        lingua_franca.load_language('en')
        # should default to the default lang with no input
        self.assertEqual(lingua_franca.get_primary_lang_code(), 'en')
        with self.assertRaises(TypeError):
            lingua_franca.get_primary_lang_code(12)
        unload_all_languages()

    def test_full_lang_code(self):
        unload_all_languages()
        self.assertEqual(lingua_franca.get_default_lang(), None)
        # Return default full lang code if no primary code is passed
        lingua_franca.load_language('en')
        self.assertEqual(lingua_franca.get_full_lang_code(), 'en-us')

        lingua_franca.load_language('es')
        lingua_franca.set_default_lang('es')
        self.assertEqual(lingua_franca.get_full_lang_code(), 'es-es')

        # Go look up the default full code for a provided primary code
        self.assertEqual(lingua_franca.get_full_lang_code('de'), 'de-de')
        # Fail on wrong type, or language not recognized
        with self.assertRaises(TypeError):
            lingua_franca.get_full_lang_code(12)

# TODO remove this test and replace with the one below as soon as practical
        self.assertWarns(DeprecationWarning,
                         lingua_franca.get_full_lang_code,
                         "bob robertson")

# TODO this is the version of the test we should use once invalid lang
# params are deprecated:
#
#        with self.assertRaises(
#                lingua_franca.internal.UnsupportedLanguageError):
#            lingua_franca.get_full_lang_code("bob robertson")
        unload_all_languages()
