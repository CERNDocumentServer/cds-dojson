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
"""Common fields."""

from __future__ import absolute_import, print_function

from dojson.utils import (IgnoreKey, filter_values, for_each_value, force_list,
                          ignore_value)

from ..models.base import model
from .utils import build_contributor, build_contributor_from_508


@model.over('recid', '^001')
def recid(self, key, value):
    """Record Identifier."""
    return int(value)


@model.over('agency_code', '^003')
def agency_code(self, key, value):
    """Control number identifier."""
    return 'SzGeCERN'


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


@model.over('contributors', '^(100|700|508)__')
def contributors(self, key, value):
    """Contributors."""
    authors = self.get('contributors', [])
    if key in ['100__', '700__']:
        items = build_contributor(value)
    else:
        items = build_contributor_from_508(value)
    # add only contributors that are not part of the authors
    if items:
        authors.extend(
            [item for item in items if item and item not in authors]
        )
    return authors


@model.over('title', '^245_[1_]')
@filter_values
def title(self, key, value):
    """Title."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
    }


@model.over('translations', '(^246_[1_])|(590__)')
@ignore_value
def translations(self, key, value):
    """Translations."""
    translation = self.get('translations', [{}])[0]
    if key.startswith('246'):
        translation['title'] = {'title': value.get('a')}
    if key.startswith('590'):
        translation['description'] = value.get('a')
    translation['language'] = 'fr'
    self['translations'] = [translation]
    raise IgnoreKey('translations')


@model.over('description', '^520__')
def description(self, key, value):
    """Description."""
    return value.get('a')


@model.over('keywords', '^6531_')
@for_each_value
@filter_values
def keywords(self, key, value):
    """Keywords."""
    return {
        'name': value.get('a'),
        'source': value.get('9') or value.get('g'),  # Easier to solve here
    }


@model.over('videos', '^774')
@for_each_value
def videos(self, key, value):
    """Videos."""
    return {
        '$ref': value.get('u')
    }


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


@model.over('license', '^540__')
@for_each_value
@filter_values
def license(self, key, value):
    """License."""
    return {
        'license': value.get('a'),
        'material': value.get('3'),
        'url': value.get('u'),
    }


@model.over('note', '^(5904_|500__)')
def note(self, key, value):
    """Note."""
    return value.get('a')


@model.over('original_source', '^541__')
def original_source(self, key, value):
    """Original source."""
    return value.get('e')


@model.over('external_system_identifiers', '^970__')
@for_each_value
def external_system_identifiers(self, key, value):
    """External unique identifiers."""
    value = value.get('a', '')
    return {
        'value': value,
        "schema": 'ALEPH' if value.startswith('0000') else value[:3]
    }


@model.over('modified_by', '^937__')
@ignore_value
def modified_by(self, key, value):
    """Modified by."""
    return value.get('s')
