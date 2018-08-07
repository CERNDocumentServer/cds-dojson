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
"""Common videos fields."""
from __future__ import absolute_import, print_function

from dojson.utils import force_list

from ...fields.utils import build_contributor, build_contributor_from_508
from ...models.base import model


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
