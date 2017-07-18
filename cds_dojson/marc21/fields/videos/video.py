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
import arrow

from dojson.errors import IgnoreKey
from dojson.utils import filter_values, force_list, \
    ignore_value

from ...models.videos.video import model
from .utils import language_to_isocode


# Required fields

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


# Language

@model.over('language', '^041__')
def language(self, key, value):
    """Language."""
    return language_to_isocode(value.get('a'))


# Rest

@model.over('physical_medium', '^340__')
@filter_values
def physical_medium(self, key, value):
    """Physical medium."""
    return {
        'camera': value.get('d'),
        'medium_standard': value.get('a'),
        'note': value.get('j')
    }


@model.over('_project_id', '^773__')
@ignore_value
def project_id(self, key, value):
    """Report number."""
    values = force_list(value)
    project_id = None
    related_links = self.get('related_links', [])
    for value in values:
        related_link = {}
        if 'p' in value and 'u' in value:
            related_link['name'] = value.get('p')
            related_link['url'] = value.get('u')
            related_links.append(related_link)
        else:
            project_id = value.get('r')
    if related_links:
        self['related_links'] = related_links
    if not project_id:
        raise IgnoreKey('project_id')
    return project_id


@model.over('location', '^110__')
def location(self, key, value):
    """Location."""
    return value.get('a')


@model.over('internal_note', '^595__')
def internal_note(self, key, value):
    """Internal note."""
    return ", ".join(filter(None, [value.get('a'), value.get('s')]))


@model.over('subject', '^65017')
def subject(self, key, value):
    """Subject."""
    return {
        'source': value.get('2', 'SzGeCERN'),
        'term': value.get('a')
    }


@model.over('accelerator_experiments', '^693__')
@filter_values
def accelerator_experiments(self, key, value):
    """Accelerator experiments."""
    return {
        'accelerator': value.get('a'),
        'experiment': value.get('e'),
        'study': value.get('s'),
        'facility': value.get('f'),
        'project': value.get('p'),
    }


@model.over('date', '^269__')
def date(self, key, value):
    """Date."""
    return arrow.get(value.get('c')).strftime('%Y-%m-%d')
