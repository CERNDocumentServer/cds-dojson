# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017 CERN.
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
"""Video fields."""

from __future__ import absolute_import, print_function

import re

from dojson.utils import filter_values, for_each_value, force_list

from ...models.videos.video import model
from .utils import build_contributor, language_to_isocode


# Required fields

@model.over('title', '^245_[1_]')
@filter_values
def title(self, key, value):
    """Title."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
    }


@model.over('description', '^520__')
def description(self, key, value):
    """Description."""
    return value.get('a')


@model.over('date', '^269__')
def date(self, key, value):
    """Date."""
    return value.get('c')


@model.over('contributors', '^(100|700)__')
def contributors(self, key, value):
    """Contributors."""
    authors = self.get('contributors', [])
    values = force_list(value)
    for value in values:
        authors.extend(build_contributor(value))
    return authors


@model.over('report_number', '^(037|088)__')
@for_each_value
def report_number(self, key, value):
    """Report number.

    Category and type are also derived from the report number.
    """
    rn = value.get('a') or value.get('9')
    if rn and key.startswith('037__'):
        # Extract category and type only from main report number, i.e. 037__a
        self['category'], self['type'] = rn.split('-')[:2]

    return rn


@model.over('duration', '^300__')
def duration(self, key, value):
    """Duration.

    The new duration must be expressed in the form hh:mm:ss[.mmm], if it isn't,
    i.e. '2 min.', we will extract it programatically later to avoid the hassle
    off dealing with more regex.
    """
    try:
        return re.match('(\d{2}:\d{2}:\d{2})(\.\d+)?', value.get('a')).group(1)
    except AttributeError:
        # The regex didn't match, we will extract the duration later.
        return None


# Access

@model.over('_access', '(^859__)|(^506[1_]_)')
def access(self, key, value):
    """Access rights.

    It includes read/update access.
    - 859__f contains the email of the submitter.
    - 506__m/5061_d list of groups or emails of people who can access the
      record. The groups are in the form <group-name> [CERN] which needs to be
      transform into the email form.
    """
    _access = self.get('_access', {})
    for value in force_list(value):
        if key == '859__' and 'f' in value:
            _access.setdefault('update', [])
            _access['update'].append(value.get('f'))
        elif key.startswith('506'):
            _access.setdefault('read', [])
            _access['read'].extend([
                s.replace(' [CERN]', '@cern.ch')
                for s in force_list(value.get('d') or value.get('m', '')) if s
            ])
    return _access


# Language

@model.over('language', '^041__')
def language(self, key, value):
    """Language."""
    return language_to_isocode(value.get('a'))
