# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2015 CERN.
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

"""Utilities for converting MARC21."""

from dojson.contrib.marc21.utils import create_record, split_stream


def load(source):
    """Load MARC XML and return Python dict."""
    for data in split_stream(source):
        record = create_record(data)
        # if record.get('999__', {}).get('a', '') == 'ALBUM':
        #     for rrecord in split_album(record):
        #         yield rrecord
        yield record


def split_album(record):
    """Create one album and several photos from the current record."""
    # TODO: Implement album splitter!
    yield record
