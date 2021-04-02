### DO NOT CHANGE THIS IMPORT ORDER ###
from .internal import get_active_langs, get_supported_locs, \
        get_full_lang_code, get_supported_langs, get_default_loc, \
        get_primary_lang_code

from .configuration import Config

### END OF IMPORT ORDER ###

from .internal import get_default_lang, set_default_lang, \
    _set_active_langs, resolve_resource_file, \
    load_language, load_languages, unload_language, unload_languages


config = Config()
