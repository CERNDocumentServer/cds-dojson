# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018, 2019 CERN.
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
"""Book utils."""

import re

from cds_dojson.marc21.fields.books.errors import MissingRequiredField

MAX_PAGES_NUMBER = 8192

RE_STR_VOLUME_PREFIX = r'(?:(?:[Vv](?:ol(?:ume)?)?|[Pp](?:art(?:ie)?|t)?|[Tt](?:eil)?|[Bb]d|[Tt]ome?|course|conference|fasc(?:icule)?|book|unit|suppl|Tafeln|Tomo)[\s\.]*)'
RE_STR_ROMAN_NUMERAL = r'(?:(?:IX|IV|V?I{1,3})|X{1,3}(?:IX|IV|V?I{0,3}))'
RE_STR_VOLUME_SUFFIX = r'(\d{{1,4}}|\d\d?[a-zA-Z]|[a-zA-Z]\d|[A-H]|{})'.format(RE_STR_ROMAN_NUMERAL)
RE_STR_VOLUME = r'(?:{}?{})'.format(RE_STR_VOLUME_PREFIX, RE_STR_VOLUME_SUFFIX)
RE_STR_SPECIAL = r'[^0-9A-Za-zÀ-ÿ\-/]'

RE_VOLUME_NUMBER = re.compile(r'(?:^|{}){}(?:$|{})'.format(RE_STR_SPECIAL, RE_STR_VOLUME, RE_STR_SPECIAL))
RE_VOLUME_INFO = re.compile(r'(.*?)\({}\)'.format(RE_STR_VOLUME))


def is_excluded(value):
    """Validate if field 300 should be excluded."""
    exclude = [
        "mul. p",
        "mult p",
        "mult. p",
        "mult. p.",
        "mult. p",
        "multi p",
        "multi pages",
    ]
    if not value or value.strip().lower() in exclude:
        return True
    return False


def extract_number_of_pages(value):
    """Extract number of pages from 300 if exists."""
    res = re.findall(r"([0-9]+) *p", value, flags=re.IGNORECASE)

    # If we have more than one occurency of pages its UnexpectedValue
    if len(res) == 1 and int(res[0]) < MAX_PAGES_NUMBER:
        return int(res[0])
    return None


def extract_physical_description(value):
    """Extract physical description from 300 if any."""
    res = re.findall(
        r"([0-9]+ \w[CD\-ROM|DVD\-ROM|diskette|VHS]+)",
        value,
        flags=re.IGNORECASE
    )
    if res:
        return ", ".join(res).upper()
    return None


def extract_parts(value):
    """Split our input to several parts."""
    separators = ["+", ";", ",", ":"]
    res = []
    for sep in separators:
        if sep in value:
            res += value.split(sep)

    valid_parts_count = len(list(filter(is_excluded, res)))

    number_of_pages = extract_number_of_pages(value)
    if number_of_pages:
        valid_parts_count -= 1

    physical_description = extract_physical_description(value)
    if physical_description:
        valid_parts_count -= len(physical_description.split(','))

    return {
        "has_extra": bool(valid_parts_count > 0),
        "number_of_pages": number_of_pages,
        "physical_copy_description": physical_description,
    }


def extract_volume_number(value, search=False, raise_exception=False,
                          subfield=None):
    """Extract the volume number from a string, returns None if not matched."""
    regex = RE_VOLUME_NUMBER
    if search:
        func = regex.search
    else:
        func = regex.match

    result = func(value.strip())
    if result:
        return result.group(1)

    if raise_exception:
        raise MissingRequiredField(
            subfield=subfield, message=' failed to parse volume number')

    return None


def extract_volume_info(value):
    """Extract ISBN, volume number and physical description from 020__u."""
    result = RE_VOLUME_INFO.search(value.strip())
    if result:
        return dict(
            description=result.group(1).strip(),
            volume=result.group(2),
        )
    return None
