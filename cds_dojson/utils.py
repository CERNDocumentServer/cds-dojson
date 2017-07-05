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
from collections import MutableMapping, MutableSequence, defaultdict

import arrow
import six


class MementoDict(dict):
    """Dictionary that remembers which keys have being access."""

    def __init__(self, *args, **kwargs):
        """Set memory and create the dictionary."""
        self.memory = set()
        if args and isinstance(args[0], MutableSequence):
            args = list(args)
            d = {}
            for k, v in args[0]:
                if k in d:
                    try:
                        d[k].append(v)
                    except AttributeError:
                        d[k] = [d[k], v]
                else:
                    d[k] = v
            args[0] = [(k, v) for k, v in six.iteritems(d)]

        super(MementoDict, self).__init__(*args, **kwargs)

    def iteritems(self, skyp_memento=False):
        """Add to memory the keys while iterating if not skyp."""
        for key, value in six.iteritems(super(MementoDict, self)):
            if not skyp_memento:
                self.memory.add(key)
            yield (key, value)

    items = iteritems

    def __getitem__(self, key):
        """Add the key to memory before running the get."""
        self.memory.add(key)
        return super(MementoDict, self).__getitem__(key)

    def get(self, key, default=None):
        """Add the key to memory before running the get."""
        self.memory.add(key)
        return super(MementoDict, self).get(key, default)

    @property
    def accessed_keys(self):
        """Get the list of accessed keys."""
        return self.memory

    @property
    def not_accessed_keys(self):
        """Get l the list of non-accessed keys."""
        return set(self.keys()).difference(self.memory)


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
    if isinstance(blob, MutableMapping):
        missing = blob.not_accessed_keys
        for key, value in blob.iteritems(skyp_memento=True):
            partial_missing = not_accessed_keys(value)
            if partial_missing:
                missing.update(
                    ['{0}{1}'.format(key, f) for f in partial_missing])
                if key in missing:
                    missing.remove(key)
    elif isinstance(blob, MutableSequence):
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
