import json

from lingua_franca import get_active_langs, get_supported_locs, \
    get_supported_langs, get_primary_lang_code, get_full_lang_code, \
    get_default_loc
from lingua_franca.internal import resolve_resource_file

default_global_values = \
    {
        'load_langs_on_demand': False
    }


class LangConfig(dict):
    def __init__(self, lang_code):
        super().__init__()
        if lang_code not in get_supported_locs():
            # DO NOT catch UnsupportedLanguageError!
            # If this fails, we want to crash. This can *only* result from
            # someone trying to override sanity checks upstairs. There are no
            # circumstances under which this should fail and allow the program
            # to continue.
            lang_code = get_full_lang_code(lang_code)

        resource_file = resolve_resource_file(f'text/{lang_code}/config.json')
        try:
            with open(resource_file, 'r', encoding='utf-8') as i_file:
                default_values = json.load(i_file)
            for k in default_values:
                self[k] = default_values[k]
        except (FileNotFoundError, TypeError):
            pass


class Config(dict):
    def __init__(self):
        super().__init__()
        self['global'] = dict(default_global_values)
        for lang in get_active_langs():
            self.load_lang(lang)

    def load_lang(self, lang):
        if all((lang not in get_supported_locs(),
                lang in get_supported_langs())):
            if lang not in self.keys():
                self[lang] = {}
                self[lang]['universal'] = LangConfig(lang)

            full_loc = get_full_lang_code(lang)
        else:
            full_loc = lang
            lang = get_primary_lang_code(lang)

        self[lang][full_loc] = LangConfig(full_loc)

    def _find_setting(self, setting=None, lang=''):
        if setting is None:
            raise ValueError("lingua_franca.config requires "
                             "a setting parameter!")

        setting_available_in = []
        possible_locs = []

        while True:
            if setting in self['global']:
                setting_available_in.append('global')
            if lang == 'global':
                break

            lang = lang or get_default_loc()

            if lang in get_supported_langs():
                possible_locs.append((lang, 'universal'))
                possible_locs.append((lang, get_full_lang_code(lang)))

            if lang in get_supported_locs():
                primary_lang_code = get_primary_lang_code(lang)
                possible_locs.append((primary_lang_code, 'universal'))
                possible_locs.append(
                    (primary_lang_code, get_default_loc(primary_lang_code)))
                possible_locs.append((primary_lang_code, lang))

            for place in possible_locs:
                if setting in self[place[0]][place[1]]:
                    setting_available_in.append(place)

            break
        try:
            return setting_available_in[-1]
        except IndexError:
            return None

    def get(self, setting=None, lang=''):
        if lang != 'global':
            if all((lang,
                    get_primary_lang_code(lang) not in get_active_langs())):
                raise ModuleNotFoundError(f"{lang} is not currently loaded")

        try:
            setting_location = self._find_setting(setting, lang)

            if setting_location == 'global':
                return self['global'][setting]
            return self[setting_location[0]][setting_location[1]][setting]

        except TypeError:
            return None

    def set(self, setting=None, value=None, lang='global'):
        if lang == 'global':
            if setting in self['global']:
                self['global'][setting] = value
                return

        setting_location = self._find_setting(setting, lang if lang !=
                                              'global' else get_default_loc())
        if all((setting_location, setting_location != 'global')):
            self[setting_location[0]][setting_location[1]][setting] = value
            return

        raise KeyError(
            f"{setting} is not available as a setting for language: '{lang}'")
