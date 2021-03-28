# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Video utils."""

import pycountry


def language_to_isocode(lang):
    """Translate language to isocode."""
    lang = lang.lower()
    try:
        return pycountry.languages.get(alpha_3=lang).alpha_2
    except (KeyError, AttributeError):
        exceptions = {
            'chi': 'zh',
            'cze': 'cs',
            'dut': 'nl',
            'eng-fre': 'en-fr',
            'fre': 'fr',
            'ger': 'de',
            'gre': 'el',
            'sil': 'silent',
            'silent': 'silent',
            'sl': 'sl',
            'sr': 'sr',
        }
        value = exceptions.get(lang)
        if value:
            return value
        try:
            return pycountry.languages.get(alpha_2=lang[0:2]).alpha_2
        except (KeyError, AttributeError):
            # FIXME log somewhere
            return 'silent'
