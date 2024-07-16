# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2015, 2017 CERN.
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

import json
import os

import pytest
from dojson.utils import filter_values

from cds_dojson.marc21.fields.books.errors import MissingRequiredField
from cds_dojson.marc21.fields.books.utils import (
    extract_volume_info,
    extract_volume_number,
)
from cds_dojson.utils import (
    MementoDict,
    convert_date_to_iso_8601,
    for_each_squash,
    not_accessed_keys,
    yaml2json,
)


def test_for_each_squash():
    """Check if for_each_squash works correctly."""

    @for_each_squash
    @filter_values
    def field(self, key, value):
        return {'a': value.get('1'), 'b': value.get('2')}

    squashed = field(None, None, {'1': 'foo', '2': 'bar'})
    assert squashed == {'a': 'foo', 'b': 'bar'}

    squashed = field(None, None, [{'1': 'foo'}, {'2': 'bar'}])
    assert squashed == {'a': 'foo', 'b': 'bar'}

    squashed = field(None, None, [{'1': 'foo', '2': 'bar2'}, {'2': 'bar'}])
    assert squashed == {'a': 'foo', 'b': ['bar2', 'bar']}


def test_convert_date_to_iso_8601():
    """Check if convert_date_to_iso_8601 works correctly"""
    string_dates = ('14/12/1989', '2013-11-22', '1999', 'Sep 1970',
                    '08 May 2002', '25 Feb 2009', '13 Dec 2002',
                    '23 August 2005', '1989/12/14', '10/09/13', '', None, )
    iso_dates = ('1989-12-14', '2013-11-22', '1999-01-01', '1970-09-01',
                 '2002-05-08', '2009-02-25', '2002-12-13', '2005-08-23',
                 '1989-12-14', '2013-09-10', '', None, )

    for string_date, iso_date in zip(string_dates, iso_dates):
        assert convert_date_to_iso_8601(string_date) == iso_date


def test_not_accessed_keys():
    """Check not_accessed_keys function."""

    d1 = MementoDict([])
    assert not not_accessed_keys(d1)

    d1 = MementoDict([('a', [1, 2, 3])])
    assert not_accessed_keys(d1) == {'a'}

    d1 = MementoDict([
        ('a', [1, 2, 3]),
        ('b', MementoDict({'1': 1}))
    ])
    assert not_accessed_keys(d1) == {'a', 'b1'}

    d1 = MementoDict([
        ('a', [1, 2, 3]),
        ('b', MementoDict({'1': 1})),
        ('c', 1)
    ])
    assert not_accessed_keys(d1) == {'a', 'b1', 'c'}

    d1 = MementoDict([
        ('a', [1, 2, 3]),
        ('b', MementoDict({'1': 1})),
        ('c', 1),
        ('d', [MementoDict({'1': 1, '2': 2}), MementoDict({'1': 2, '2': 2})])
    ])
    assert not_accessed_keys(d1) == {'a', 'b1', 'c', 'd1', 'd2'}

    assert not d1.accessed_keys

    d1['d'][0]['1']
    assert not_accessed_keys(d1) == {'a', 'b1', 'c', 'd1', 'd2'}
    d2 = d1.get('b')
    assert not_accessed_keys(d1) == {'a', 'b1', 'c', 'd1', 'd2'}

    for k, v in d2.iteritems():
        pass
    assert not_accessed_keys(d1) == {'a', 'c', 'd1', 'd2'}

    d1.get('c')
    assert not_accessed_keys(d1) == {'a', 'd1', 'd2'}

    d1 = MementoDict([
        ('a', [1, 2, 3]),
        ('b', MementoDict({'1': 1})),
        ('c', 1),
        ('d', [MementoDict({'1': 1, '2': 2}), MementoDict({'1': 2, '2': 2})]),
        ('e', MementoDict([('1', 1), ('1', 2), ('1', 3)]))
    ])
    assert not_accessed_keys(d1) == {'a', 'b1', 'c', 'd1', 'd2', 'e1'}


def test_memento_dict():
    """Check MementoDict class."""

    d = MementoDict({'a': 1, 'b': 2})
    assert d == {'a': 1, 'b': 2}

    d = MementoDict([('a', 1), ('b', 2)])
    assert d == {'a': 1, 'b': 2}

    d = MementoDict([('a', 1), ('a', 2)])
    assert d == {'a': [1, 2]}

    # NOTE: is this the expected behavior?
    d = MementoDict([('a', 1), ('a', [2, 3])])
    assert d == {'a': [1, 2, 3]}


def test_yaml2json():
    """Test yaml to json file conversion"""

    root_dir = './tests/fixtures/books/'
    source = os.path.join(root_dir, 'ymls/')
    destination = os.path.join(root_dir, 'results')

    yaml2json(source, destination)

    with open(os.path.join(root_dir, 'books_title_mock.json')) as s:
        # read the mock JSON file
        json_mock = json.load(s)

    assert os.path.exists(destination)

    with open(os.path.join(destination, 'books_title.json')) as s:
        # read the newly created JSON file
        json_converted = json.load(s)

    assert json_mock == json_converted


volume_params = [
    ('v1', '1', False),
    ('v 1', '1', False),
    ('v.1', '1', False),
    ('v. 1', '1', False),
    ('v . 1', '1', False),
    ('vol.1', '1', False),
    ('Vol. 2', '2', False),
    ('voL . 1', None, False),
    ('volume.1', '1', False),
    ('Volume. 1', '1', False),
    ('volume . 3', '3', False),
    ('pt 5', '5', False),
    ('part 5', '5', False),
    ('par 5', None, False),
    ('v. A', 'A', False),
    ('val. 5', None, False),
    ('part III', 'III', False),
    ('March 1996', None, False),
]


@pytest.mark.parametrize('value, expected, raise_exception', volume_params)
def test_extract_volume_number(value, expected, raise_exception):
    """Test extracting volume number."""
    if raise_exception:
        with pytest.raises(MissingRequiredField):
            assert extract_volume_number(
                value,
                raise_exception=raise_exception
            ) == expected
    else:
        assert extract_volume_number(value) == expected


volume_info_params = [
    (
        'print version, paperback ({})'.format(vol_str),
        dict(volume=expected, description='print version, paperback') if expected else None
    )
    for vol_str, expected, raise_exception in volume_params
]
volume_info_params.append(('print version, paperback v.5', None))


@pytest.mark.parametrize('value, expected', volume_info_params)
def test_extract_volume_info(value, expected):
    """Test extracting volume info."""
    assert extract_volume_info(value) == expected
