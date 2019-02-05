# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018, 2019 CERN.
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
"""Book utils."""

import re


def is_excluded(value):
    """Validate if field 300 should be excluded."""
    exclude = ['mult. p', 'mult p']
    if value in exclude:
        return True
    return False


def extract_page_number(value):
    """Extract page number from 300 if exists."""
    num_search = re.search(r'(^[0-9]+) *p', value)
    if num_search:
        return int(num_search.group(1))
    return None


def extract_physical_description(value):
    """Extract extra information from 300 if any."""
    separators = ['+', ';', ',', ':']
    result = []
    for sep in separators:
        if sep in value:
            result += value.split(sep)

    has_number = extract_page_number(value)
    if has_number:
        return ','.join(result[1:])
    elif result:
        return ','.join(result[0:])
    return value
