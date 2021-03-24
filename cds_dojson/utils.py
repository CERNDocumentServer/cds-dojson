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
"""The CDS DoJson Utils."""

import functools
from collections import defaultdict

import arrow
import six
from dojson.utils import GroupableOrderedDict


class MementoDict(GroupableOrderedDict):
    """Dictionary that remembers which keys have being access."""

    def __new__(cls, *args):
        """Add the memory to the default instance."""
        cls.accessed_keys = property(
            lambda self: set([k for k in self.__memory if k != '__order__']))
        cls.not_accessed_keys = property(
            lambda self: set(
                [k for k in self.keys() if k != '__order__']
            ).difference(self.__memory))
        new = GroupableOrderedDict.__new__(cls, *args)
        new.__memory = set()
        new.__skip_memento = False
        return new

    def iteritems(self, skip_memento=False, **kwargs):
        """Add to memory the keys while iterating if not skyp."""
        self.__skip_memento = skip_memento
        for key, value in super(MementoDict, self).iteritems(**kwargs):
            self._add_to_memory(key)
            yield (key, value)
        self.__skip_memento = False

    items = iteritems

    def __repr__(self):
        """Output the representation of the GroupableOrderedDict."""
        out = ("({!r}, {!r})".format(k, v)
               for k, v in self.iteritems(skip_memento=True, repeated=True)
               if k != '__order__')
        return 'GroupableOrderedDict(({out}))'.format(out=', '.join(out))

    def _add_to_memory(self, key):
        """Add key to the memory is it is not locked."""
        if not self.__skip_memento:
            self.__memory.add(key)

    def __getitem__(self, key):
        """Add the key to memory before running the get."""
        self._add_to_memory(key)
        return super(MementoDict, self).__getitem__(key)

    def get(self, key, default=None):
        """Add the key to memory before running the get."""
        self._add_to_memory(key)
        return super(MementoDict, self).get(key, default)


def for_each_squash(f):
    """In case of non repeatable field squash them into one.

    .. example::
        [{'a': 'foo'}, {'b': 'bar'}] -> {'a': 'foo', 'b': 'barc'}
        [{'a': 'foo'}, {'a': 'bar'}] -> {'a': ['foo', 'barc']}
    """
    @functools.wraps(f)
    def wrapper(self, key, values, **kwargs):
        if not isinstance(values, list):
            return f(self, key, values, **kwargs)

        unmerged_list = [f(self, key, value, **kwargs) for value in values]
        merge_dict = defaultdict(list)

        for unmerged_dict in unmerged_list:
            for key, element in six.iteritems(unmerged_dict):
                merge_dict[key].append(element)

        merge_dict = {
            key: (value if len(value) > 1 else value[0])
            for key, value in six.iteritems(merge_dict)
        }
        return merge_dict

    return wrapper


def not_accessed_keys(blob):
    """Calculate not accessed keys from the blob.

    It assumes the blob is an instance of MementoDict or a list.
    """
    missing = set()
    if isinstance(blob, dict):
        missing = blob.not_accessed_keys
        for key, value in blob.iteritems(skip_memento=True):
            partial_missing = not_accessed_keys(value)
            if partial_missing:
                missing.update(
                    ['{0}{1}'.format(key, f) for f in partial_missing])
                if key in missing:
                    missing.remove(key)
    elif isinstance(blob, (tuple, list)):
        for value in blob:
            missing.update(not_accessed_keys(value))

    return missing


def convert_date_to_iso_8601(date, format_='YYYY-MM-DD', **kwargs):
    """Convert a date string its ISO 8601 representation.

    YYYY-MM-DDThh:mm:ss.sTZD (eg 1997-07-16T19:20:30.45+01:00)

    YYYY = four-digit year
    MM   = two-digit month (01=January, etc.)
    DD   = two-digit day of month (01 through 31)
    hh   = two digits of hour (00 through 23) (am/pm NOT allowed)
    mm   = two digits of minute (00 through 59)
    ss   = two digits of second (00 through 59)
    s    = one or more digits representing a decimal fraction of a second
    TZD  = time zone designator (Z or +hh:mm or -hh:mm)
    """
    # The order is important as arrow tries to apply them top to bottom
    _FORMATS = [
        'YYYY-MM-DD',
        'YYYY/MM/DD',
        'DD/MM/YYYY',
        'DD/MM/YY',
        'YYYY.MM.DD',
        'DD MMMM YYYY',
        'DD MMM YYYY',
        'DD MMM YY',
        'YYYY-MM',
        'YYYY/MM',
        'YYYY.MM',
        'MMM YYYY',
        'YYYY',
        'YY',
    ]
    return arrow.get(date, _FORMATS).format(format_) if date else date
