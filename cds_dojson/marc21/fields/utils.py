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

from __future__ import absolute_import, print_function

import copy
import functools
import re
from datetime import date, timedelta
from itertools import chain

import requests
from dojson.errors import IgnoreKey
from dojson.utils import force_list
from six import PY2, iteritems

from cds_dojson.marc21.fields.books.errors import (
    ManualMigrationRequired,
    MissingRequiredField,
    UnexpectedValue,
)
from cds_dojson.utils import MementoDict


# TODO to be decided where is the config value for domain
def related_url(value):
    """Builds related records urls."""
    return '{0}{1}'.format('https://cds.cern.ch/record/', value)


def clean_pages_range(pages_subfield, value):
    """Builds pages dictionary."""
    page_regex = r'\d+(?:[\-‐‑‒–—―⁻₋−﹘﹣－]*\d*)$'
    pages_val = clean_val(pages_subfield, value, str, regex_format=page_regex)
    if pages_val:
        pages = re.split(r'[\-‐‑‒–—―⁻₋−﹘﹣－]+', pages_val)
        if len(pages) == 1:
            result = {'page_start': int(pages[0])}
            return result
        else:
            result = {'page_start': int(pages[0]),
                      'page_end': int(pages[1])}
            return result


def clean_str(to_clean, regex_format, req, transform=None):
    """Cleans string marcxml values."""
    if regex_format:
        pattern = re.compile(regex_format)
        match = pattern.match(to_clean)
        if not match:
            raise UnexpectedValue
    try:
        cleaned = to_clean.strip()
    except AttributeError:
        raise UnexpectedValue
    if not cleaned and req:
        raise MissingRequiredField
    if transform and hasattr(cleaned, transform):
        cleaned = getattr(cleaned, transform)()
    return cleaned


def clean_val(subfield, value, var_type, req=False, regex_format=None,
              default=None, manual=False, transform=None):
    """
    Tests values using common rules.

    :param subfield: marcxml subfield indicator
    :param value: mxrcxml value
    :param var_type: expected type for value to be cleaned
    :param req: specifies if the value is required in the end schema
    :param regex_format: specifies if the value should have a pattern
    :param default: if value is missing and required it outputs default
    :param manual: if the value should be cleaned manually durign the migration
    :param transform: string transform function
    :return: cleaned output value
    """
    to_clean = value.get(subfield)
    if manual and to_clean:
        raise ManualMigrationRequired
    if req and to_clean is None:
        if default:
            return default
        raise MissingRequiredField
    if to_clean is not None:
        try:
            if var_type is str:
                return clean_str(to_clean, regex_format, req, transform)
            elif var_type is bool:
                return bool(to_clean)
            elif var_type is int:
                return int(to_clean)
            else:
                raise NotImplementedError
        except ValueError:
            raise UnexpectedValue(subfield=subfield)
        except TypeError:
            raise UnexpectedValue(subfield=subfield)


def clean_email(value):
    """Cleans the email field."""
    if value:
        email = value.strip().replace(' [CERN]', '@cern.ch'). \
            replace('[CERN]', '@cern.ch')
        return email


def get_week_start(year, week):
    """Translates cds book yearweek format to starting date."""
    d = date(year, 1, 1)
    if d.weekday() > 3:
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return d + dlt


def replace_in_result(phrase, replace_with, key=None):
    """Replaces string values in list with given string."""

    def the_decorator(fn_decorated):
        def proxy(*args, **kwargs):
            res = fn_decorated(*args, **kwargs)
            if res:
                if not key:
                    return [k.replace(phrase, replace_with).strip()
                            for k in res]
                else:
                    return [dict((k, v.replace(phrase, replace_with).strip()
                                  if k == key else v
                                  )
                                 for k, v in elem.items()) for elem in res]
            return res

        return proxy

    return the_decorator


def filter_list_values(f):
    """Remove None and blank string values from list of dictionaries."""

    @functools.wraps(f)
    def wrapper(self, key, value, **kwargs):
        out = f(self, key, value)
        if out:
            print(out)
            clean_list = [dict((k, v) for k, v in elem.items()
                               if v) for elem in out if elem]
            clean_list = [elem for elem in clean_list if elem]
            if not clean_list:
                raise IgnoreKey(key)
            return clean_list
        else:
            raise IgnoreKey(key)

    return wrapper


def out_strip(fn_decorated):
    """Decorator cleaning output values of trailing and following spaces."""

    def proxy(self, key, value, **kwargs):
        res = fn_decorated(self, key, value, **kwargs)
        if not res:
            raise IgnoreKey(key)
        if isinstance(res, str):
            # the value is not checked for empty strings here because clean_val
            # does the job, it will be None caught before
            return res.strip()
        elif isinstance(res, list):
            cleaned = [elem.strip() for elem in res if elem]
            if not cleaned:
                raise IgnoreKey(key)
            return cleaned
        else:
            return res

    return proxy


def _get_http_request(url, retry=0):
    """Get the url and retry if fails."""
    try:
        return requests.get(url).json()
    except Exception:
        if retry > 0:
            retry = retry - 1
            # FIXME use invenio-logging?
            return _get_http_request(url=url, retry=retry)


def get_author_info_from_people_collection(info):
    """Get author information from CDS auto-completion endpoint."""
    # TODO: probably we will need to extract this somewhere else
    URL = ('https://cds.cern.ch/submit/get_authors?'
           'query={0}&relative_curdir=cdslabs%2Fvideos')
    if '0' in info or not info.get('a'):
        # There is already enough information or we don't have a name to query
        return info
    author_name = info.get('a')
    if PY2:
        # In Python 3, encoded name will change type to bytes and this will
        # cause query to CDS to fail
        author_name = author_name.encode('utf-8')
    author_info = _get_http_request(url=URL.format(author_name), retry=10)
    if not author_info or len(author_info) > 1:
        # Didn't find anything or find to many matches
        return info

    # Prepare author name
    author_info = author_info[0]
    if 'name' not in author_info:
        author_info['name'] = '{0}, {1}'.format(author_info['lastname'],
                                                author_info['firstname'])
    return MementoDict([
        (k, v) for k, v in chain(info.items(), iteritems(author_info))])


def _get_correct_video_contributor_role(role):
    """Clean up roles for Videos."""
    translations = {
        '3d animation': 'Animatons by',
        '3d animations': 'Animations by',
        'animation': 'Animations by',
        'animations': 'Animations by',
        u'auteur-r\xe9alisateur': ('Creator', 'Producer'),
        'author': 'Creator',
        'autor': 'Creator',
        'camera': 'Camera Operator',
        'camera & sound': 'Camera Operator',
        'co-produced by': 'Co-Producer',
        'co-production': 'Co-Producer',
        'commentaire': 'Comments by',
        'commentaires': 'Comments by',
        'content': 'Screenwriter',
        'coordination du film': 'Editor',
        'coordination montage film': 'Editor',
        'copione & realizzazione': ('Screenwriter', 'Producer'),
        'created by': 'Creator',
        'credit': 'Credits',
        'credits': 'Credits',
        'diaporama': 'Photography',
        'dierctor': 'Director',
        'directed by': 'Director',
        'directeur de production': ('Director', 'Producer'),
        'direction and project management': ('Director', ''),
        'director': 'Director',
        'director & producer': ('Director', 'Producer'),
        'directors': 'Director',
        'direttore': 'Director',
        'ecriture': 'Screenwriter',
        'edited by': 'Editor',
        'editing': 'Editor',
        'edition': 'Editor',
        'editor': 'Editor',
        u'enqu\xeate': 'Reporter',
        'entretiens': 'Reporter',
        'executive producer': 'Producer',
        'film maker': 'Camera Operator',
        'filmed by': 'Camera Operator',
        'filmmaker': 'Camera Operator',
        'images': 'Photography',
        'images & editing': ('Photography', 'Editor'),
        'images from': 'Photography',
        'images maker': 'Photography',
        'journalist': 'Reporter',
        'konzept und herstellung': 'Producer',
        'made by': 'Creator',
        'montage': 'Editor',
        'narrator': 'Narrator',
        'presentator': 'Reporter',
        'presented by': 'Reporter',
        'presenter': 'Reporter',
        'presenter/reporter': 'Reporter',
        'produced by': 'Producer',
        'producer': 'Producer',
        'producers': 'Producer',
        'production': 'Producer',
        'production et commentaire': ('Producer', 'Comments by'),
        'productor': 'Producer',
        'realisateur': 'Producer',
        'realisation': 'Producer',
        u'r\xe9alisation': 'Producer',
        'redaktion': 'Editor',
        'related by': 'Narrator',
        'reporter': 'Reporter',
        'reports': 'Reporter',
        'scenario et realisation': 'Producer',
        'script': 'Screenwriter',
        'script & director': ('Screenwriter', 'Director'),
        'script and director': ('Screenwriter', 'Director'),
        'script, design and direction': ('Screenwriter', 'Editor', 'Director'),
        u'sc\xe9nario et r\xe9alisation': 'Producer',
        'series producer': 'Producer',
        'shooting and editing': ('Camera Operator', 'Editor'),
        'son': 'Music by',
        'speaker': 'Speaker',
        'writen by': 'Screenwriter',
        'writer and director': ('Screenwriter', 'Director'),
        'written & directed by': ('Screenwriter', 'Director'),
        'written & produced by': ('Screenwriter', 'Producer'),
        'written and director': ('Screenwriter', 'Director'),
        'written and produced by': ('Screenwriter', 'Producer'),
    }
    return translations[role.lower()]


def _get_correct_books_contributor_role(subfield, role):
    """Clean up roles."""
    translations = {
        'author': 'AUTHOR',
        'dir.': 'SUPERVISOR',
        'dir': 'SUPERVISOR',
        'ed.': 'EDITOR',
        'ed': 'EDITOR',
        'ill.': 'ILLUSTRATOR',
        'ill': 'ILLUSTRATOR',
    }
    if isinstance(role, str):
        clean_role = role.lower()
    else:
        raise UnexpectedValue(subfield=subfield, message=' unknown role')
    if clean_role not in translations:
        raise UnexpectedValue(subfield=subfield, message=' unknown role')
    return translations[clean_role]


def _extract_json_ids(info, provenence='source'):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        'AUTHOR|(INSPIRE)': 'INSPIRE ID',
        'AUTHOR|(CDS)': 'CDS',
        'AUTHOR|(SzGeCERN)': 'CERN'
    }
    regex = re.compile(r'((AUTHOR\|\((CDS|INSPIRE)\))|(\(SzGeCERN\)))(.*)')
    ids = []
    author_ids = force_list(info.get('0', ''))

    for author_id in author_ids:
        match = regex.match(author_id)
        if match:
            ids.append(
                {
                    'value': match.group(3),
                    provenence: SOURCES[match.group(1)]
                })
    # Try and get the IDs from the auto-completion
    try:
        ids.append({'value': info['cernccid'], provenence: 'CERN'})
    except KeyError:
        pass
    try:
        ids.append({'value': info['recid'], provenence: 'CDS'})
    except KeyError:
        pass
    try:
        ids.append({'value': info['inspireid'], provenence: 'INSPIRE ID'})
    except KeyError:
        pass
    return ids


def _extract_json_ils_ids(info, provenence='source'):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        'AUTHOR|(INSPIRE)': 'INSPIRE ID',
        'AUTHOR|(CDS)': 'CDS',
        'AUTHOR|(SzGeCERN)': 'CERN'
    }
    regex = re.compile(r'(AUTHOR\|\((CDS|INSPIRE|SzGeCERN)\))(.*)')
    ids = []
    author_ids = force_list(info.get('0', ''))
    for author_id in author_ids:
        match = regex.match(author_id)
        if match:
            ids.append(
                {
                    'value': match.group(3),
                    provenence: SOURCES[match.group(1)]
                })
    try:
        ids.append({'value': info['inspireid'], provenence: 'INSPIRE ID'})
    except KeyError:
        pass

    return ids


def build_contributor_books(value):
    """Create the contributors for books."""
    if not value.get('a'):
        return []

    contributor = {
        'identifiers': _extract_json_ils_ids(value, 'scheme') or None,
        'full_name': value.get('name') or clean_val('a', value, str),
        'roles': [
            _get_correct_books_contributor_role(
                'e', value.get('e', 'author'))
        ],
    }

    value_u = value.get('u')
    if value_u:
        values_u_list = list(force_list(value_u))
        other = ['et al.', 'et al']
        for x in other:
            if x in values_u_list:
                values_u_list.remove(x)
        contributor['affiliations'] = [{'name': x} for x in
                                       values_u_list]
    contributor = dict(
        (k, v) for k, v in iteritems(contributor) if v is not None
    )
    return contributor


def build_contributor_videos(value):
    """Create a.

    :returns: Contributors
    :rtype: list

    .. note::

        In some cases contributor has a tuple of roles
        (i.e. ('Producer', 'Director')) in such cases we return the contributor
        as many times as the roles (2 in the example).
    """
    OLD_VIDEO_TEAM_NAMES = {
        'cern', 'cern ', 'cern / audiovisual service', 'cern ???',
        'cern audio service', 'cern audio video service',
        'cern audio visual service', 'cern audioivisual unit',
        'cern audiovideo service', 'cern audiovisual',
        'cern audiovisual production', 'cern audiovisual production service',
        'cern audiovisual productions', 'cern audiovisual productions service',
        'cern audiovisual servic', 'cern audiovisual service',
        'cern audiovisual team', 'cern audiovisual unit',
        'cern audiovisual unit ', 'cern audiovisual unit ??',
        'cern audivisual service', 'cern av service', 'cern avc',
        'cern multimedia', 'cern multimedia production unit',
        'cern multimedia productions', 'cern production',
        'cern video procuctions', 'cern video production',
        'cern video productions', 'cern video service',
        'cern video+photo productions', 'cern videos production',
        'cern videos productions', 'cern visual media office', 'cern vmo'
    }
    if not value.get('a'):
        # Sometimes there are 100 or 700 fields with no $a subfield
        # (wrong metadata), so let's ignore them
        value.get('e')  # quick hack to avoid false positves
        return []
    if value.get('a').lower() not in OLD_VIDEO_TEAM_NAMES:
        # Avoids a few calls
        value = get_author_info_from_people_collection(value)

    role = _get_correct_video_contributor_role(
        value.get('e', 'producer'))  # always unicode
    contributors = []
    contributor = {
        'ids': _extract_json_ids(value) or None,
        'name': value.get('name') or value.get('a'),
        'affiliations': force_list(value.get('affiliation') or value.get('u')),
        'email': value.get('email'),
    }
    if contributor['name'].lower() in OLD_VIDEO_TEAM_NAMES:
        contributor['name'] = 'CERN Video Productions'

    contributor = dict(
        (k, v) for k, v in iteritems(contributor) if v is not None
    )

    if isinstance(role, tuple):
        for _role in role:
            contributor['role'] = _role
            contributors.append(copy.deepcopy(contributor))
    else:
        contributor['role'] = role
        contributors.append(contributor)
    return contributors


def build_contributor_from_508(value):
    """Build contributors from field 508."""
    item = value.get('a')
    if item.lower().startswith('camera operator'):
        if ',' in item:
            camera_operators = value.get('a').split(',')
            # remove "camera operator" from the list
            camera_operators.pop(0)
            contributors = []
            for name in camera_operators:
                contributor = build_contributor_videos(
                    {'a': name.strip(), 'e': 'camera'})
                if contributor:
                    contributors.append(contributor[0])
            return contributors
    else:
        return build_contributor_videos({'a': item.strip(), 'e': 'credits'})
