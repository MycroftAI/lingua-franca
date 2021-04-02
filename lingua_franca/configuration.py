import json
from os import path

from lingua_franca import get_active_langs, get_supported_locs, \
        get_supported_langs, get_primary_lang_code, get_full_lang_code, \
            get_default_loc
from lingua_franca.internal import UnsupportedLanguageError, resolve_resource_file

default_global_values = \
    {
        'load_langs_on_demand': False
    }

class LangConfig(dict):
    def __init__(self, lang_code):
        if lang_code not in get_supported_locs():
            # DO NOT catch UnsupportedLanguageError!
            # If this fails, we want to crash. This can *only* result from
            # someone trying to override sanity checks upstairs. There are no
            # circumstances under which this should fail and allow the program
            # to continue.
            lang_code = get_full_lang_code(lang_code)


        resource_file = resolve_resource_file(f'text/{lang_code}/config.json')
        with open(resource_file, 'r', encoding='utf-8') as i_file:
            default_values = json.load(i_file)
        for k in default_values:
            self[k] = default_values[k]

class Config(dict):
    def __init__(self):
        self['global'] = dict(default_global_values)
        for lang in get_active_langs():
            '''
            TODO proper full loc support here will handle languages similarly to global:

                    self['en']['universal'] for 'default' English config
                                            (all dialects if not overridden)
                    self['en']['en-us'] for overrides specific to en-US
                    self['en']['en-au'] for overrides specific to en-AU

                and so forth.
            '''
            if all((lang not in self.keys(), lang not in get_supported_locs())):
                self[lang] = {}
                self[lang]['universal'] = LangConfig(lang)
            # begin portion that will need to adapt for the todo above
            full_loc = lang if lang in get_supported_locs() else \
                get_full_lang_code(lang)
            self[lang][full_loc] = LangConfig(lang)
    
    def get(self, setting=None, lang='global'):
        if setting is None:
            raise ValueError("lingua_franca.config.get() requires "
                             "a setting parameter!")
        
        if lang is None:
            lang = get_default_loc()
        
        setting_available_in = []
        possible_locs = []

        stop = False
        while True:
            if setting in self['global']:
                setting_available_in.append('global')
            if lang == 'global':
                break

            if lang in get_supported_langs():
                possible_locs.append(self[lang]['universal'])
                possible_locs.append(self[lang][get_full_lang_code(lang)])

            if lang in get_supported_locs():
                possible_locs.append(self[get_primary_lang_code(lang)]['universal'])
                possible_locs.append(self[get_primary_lang_code(lang)][lang])
            
            for place in possible_locs:
                if setting in place:
                    setting_available_in.append(place)
            break
        try:
            return self[setting_available_in[-1]][setting]
        except KeyError as e:
            # TODO: lots of sanity checking before PR is ready
            raise e