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
"""General field utils."""

import requests
from six import iteritems
from itertools import chain

from ..utils import MementoDict


def get_author_info_from_people_collection(info):
    """Get author information from CDS auto-completion endpoint."""
    # TODO: probably we will need to extract this somewhere else
    URL = 'https://cds.cern.ch/submit/get_authors?query={0}&relative_curdir=cdslabs%2Fvideos'
    if '0' in info or not info.get('a'):
        # There is already enough information or we don't have a name to query
        return info
    author_info = requests.get(URL.format(info.get('a'))).json()
    if not author_info or len(author_info) > 1:
        # Didn't find anything or find to many matches
        return info

    # Prepare author name
    author_info = author_info[0]
    if 'name' not in author_info:
        author_info['name'] = '{0}, {1}'.format(author_info['lastname'],
                                                author_info['firstname'])
    return MementoDict([
        (k, v) for k, v in chain(info.iteritems(), iteritems(author_info))])
