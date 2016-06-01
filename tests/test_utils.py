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
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

from __future__ import absolute_import

import arrow
from dojson.utils import filter_values

from cds_dojson.utils import for_each_squash, convert_date_to_iso_8601


def test_for_each_squash():
    """Check if for_each_squash works correctly."""

    @for_each_squash
    @filter_values
    def field(self, key, value):
        return {
            'a': value.get('1'),
            'b': value.get('2')
        }

    squashed = field(None, None, {'1': 'foo', '2': 'bar'})
    assert squashed == {'a': 'foo', 'b': 'bar'}

    squashed = field(None, None, [{'1': 'foo'}, {'2': 'bar'}])
    assert squashed == {'a': 'foo', 'b': 'bar'}

    squashed = field(None, None, [{'1': 'foo', '2': 'bar2'}, {'2': 'bar'}])
    assert squashed == {'a': 'foo', 'b': ['bar2', 'bar']}


def test_convert_date_to_iso_8601():
    """Check if convert_date_to_iso_8601 works correctly"""
    string_dates = (
        '14/12/1989',
        '2013-11-22',
        '1999',
        'Sep 1970',
        '08 May 2002',
        '25 Feb 2009',
        '13 Dec 2002',
        '23 August 2005',
        '',
        None,
    )
    iso_dates = (
        '1989-12-14',
        '2013-11-22',
        '1999-01-01',
        '1970-09-01',
        '2002-05-08',
        '2009-02-25',
        '2002-12-13',
        '2005-08-23',
        '',
        None,
    )

    for string_date, iso_date in zip(string_dates, iso_dates):
        assert convert_date_to_iso_8601(string_date) == iso_date
