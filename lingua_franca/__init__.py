### DO NOT CHANGE THIS IMPORT ORDER ###
from .internal import get_active_langs, get_supported_locs, \
        get_full_lang_code

from .configuration import Config

### END OF IMPORT ORDER ###

from .internal import get_default_lang, set_default_lang, get_default_loc, \
    _set_active_langs, get_primary_lang_code, resolve_resource_file, \
    load_language, load_languages, unload_language, unload_languages, \
    get_supported_langs


config = Config()
