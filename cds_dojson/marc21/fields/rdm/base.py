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
"""Common RDM fields."""

import functools
import re
from dateutil import parser
from dojson.errors import IgnoreKey

from cds_dojson.marc21.fields.books.errors import ManualMigrationRequired, MissingRequiredField, UnexpectedValue
from cds_dojson.marc21.fields.utils import clean_val, out_strip
from cds_dojson.marc21.models.rdm.base import model
from dojson.utils import force_list
from dojson.errors import IgnoreItem, IgnoreKey



def extract_json_contributor_ids(info):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        "AUTHOR|(INSPIRE)": "INSPIRE",
        "AUTHOR|(CDS)": "CDS",
    }
    regex = re.compile(r"(AUTHOR\|\((INSPIRE|CDS)\))(.*)")
    ids = []
    author_ids = force_list(info.get("0", ""))
    for author_id in author_ids:
        match = regex.match(author_id)
        if match:
            ids.append(
                {"identifier": match.group(3), "scheme": SOURCES[match.group(1)]}
            )
    try:
        ids.append({"identifier": info["inspireid"], "scheme": "INSPIRE"})
    except KeyError:
        pass

    author_orcid = info.get("k")
    if author_orcid:
        ids.append({"identifier": author_orcid, "scheme": "ORCID"})

    return ids

def for_each_value(f, duplicates=False):
    """Apply function to each item."""
    # Extends values under same name in output.  This should be possible
    # because we are already expecting list.
    setattr(f, "__extend__", True)

    @functools.wraps(f)
    def wrapper(self, key, values, **kwargs):
        parsed_values = []

        if not isinstance(values, (list, tuple, set)):
            values = [values]

        for value in values:
            try:
                if not duplicates and value not in parsed_values:
                    parsed_values.append(f(self, key, value, **kwargs))
                elif duplicates:
                    parsed_values.append(f(self, key, value, **kwargs))
            except IgnoreItem:
                continue

        return parsed_values

    return wrapper


def require(subfields):
    """Mark required subfields in a MARC field."""

    def the_decorator(fn_decorated):
        def proxy(self, key, value, **kwargs):
            for subfield in subfields:
                value.get(subfield)
                if not subfield:
                    raise MissingRequiredField(field=key, subfield=subfield)
            res = fn_decorated(self, key, value, **kwargs)
            return res

        return proxy

    return the_decorator

def get_contributor_role(subfield, role, raise_unexpected=False):
    """Clean up roles."""
    translations = {
        "author": "OTHER",
        "author.": "OTHER",
        "dir.": "SUPERVISOR",
        "dir": "SUPERVISOR",
        "supervisor": "SUPERVISOR",
        "ed.": "EDITOR",
        "editor": "EDITOR",
        "editor.": "EDITOR",
        "ed": "EDITOR",
        "ill.": "other",
        "ill": "other",
        "ed. et al.": "EDITOR",
    }
    clean_role = None
    if role is None:
        return "other"
    if isinstance(role, str):
        clean_role = role.lower()
    elif isinstance(role, list) and role and role[0]:
        clean_role = role[0].lower()
    elif raise_unexpected:
        raise UnexpectedValue(subfield=subfield, message="unknown author role")

    if clean_role not in translations or clean_role is None:
        return "other"

    return translations[clean_role].lower()

def strip_output(fn_decorated):
    """Decorator cleaning output values of trailing and following spaces."""

    def proxy(self, key, value, **kwargs):
        res = fn_decorated(self, key, value, **kwargs)
        if not res:
            raise IgnoreKey(key)
        if isinstance(res, str):
            return res.strip()
        elif isinstance(res, list):
            cleaned = [elem.strip() for elem in res if elem]
            if not cleaned:
                raise IgnoreKey(key)
            return cleaned
        else:
            return res

    return proxy


@model.over('preprint_date', '^269__')     # item, RDM?!
@out_strip
def preprint_date(self, key, value):
    """Translates preprint_date fields."""
    date = clean_val('c', value, str)
    if date:
        try:
            date = parser.parse(date)
            return date.date().isoformat()
        except (ValueError, AttributeError):
            raise ManualMigrationRequired(subfield='c')
    else:
        raise IgnoreKey('preprint_date')
    
@model.over('publication_date', '^260__')
@out_strip
def publication_date(self, key, value):
    """Translates publication_date fields."""
    # import pdb; pdb.set_trace()
    date = clean_val('c', value, str)
    if date:
        try:
            date = parser.parse(date)
            return date.date().isoformat()
        except (ValueError, AttributeError):
            raise ManualMigrationRequired(subfield='c')
    else:
        raise IgnoreKey('publication_date')

@model.over('report_number', '^037__')
@out_strip
def report_number(self, key, value):
    """Translates report_number fields."""
    report_number = clean_val('a', value, str)
    if report_number:
        return report_number
    else:
        raise IgnoreKey('report_number')
    
@model.over('title', '^245__')
@out_strip
def title(self, key, value):
    """Translates title fields."""
    return clean_val('a', value, str)

@model.over("creators", "^100__")
@for_each_value
@require(["a"])
def creators(self, key, value):
    """Translates the creators field."""
    role = get_contributor_role("e", value.get("e", "author"))

    contributor = {
        "person_or_org": {
            "type": "personal",
            "family_name": value.get("name") or value.get("a"), # TODO: tune name
            # "identifiers": extract_json_contributor_ids(value), # TODO: Requires CDS scheme 
        }
    }
    if role:
        contributor.update({"role": {"id": role}})  # VOCABULARY ID

    return contributor

@model.over("contributors", "^700__")
@for_each_value
@require(["a"])
def creators(self, key, value):
    """Translates the contributor field."""
    role = get_contributor_role("e", value.get("e", "author"))

    contributor = {
        "person_or_org": {
            "type": "personal",
            "family_name": value.get("name") or value.get("a"), # TODO: tune name
            # "identifiers": extract_json_contributor_ids(value), # TODO: Requires CDS scheme 
        }
    }
    if role:
        contributor.update({"role": {"id": role}})  # VOCABULARY ID

    return contributor

@model.over('legacy_recid', '^001')
def legacy_recid(self, key, value):
    """Translates legacy_recid fields."""
    return int(value)

@model.over('file_links', '^8564_')
@out_strip
def file_links(self, key, value):
    """Translates file_links fields."""
    return clean_val('u', value, str)

@model.over("description", "^520__")
@strip_output
def abstract(self, key, value):
    """Translates abstracts fields."""
    return value.get("a", "")
