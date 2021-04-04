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
from datetime import datetime, timedelta
from lingua_franca.lang.parse_common import Normalizer

from lingua_franca.internal import ConfigVar

class HungarianNormalizer(Normalizer):
    """ TODO implement language specific normalizer"""


def normalize_hu(text, remove_articles=True):
    """ English string normalization """
    return HungarianNormalizer().normalize(text, remove_articles)
