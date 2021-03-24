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

import copy
import re
from itertools import chain

import requests
from dojson.utils import force_list
from six import PY2, iteritems

from ..utils import MementoDict


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
    """Clean up roles."""
    tranlations = {
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
    return tranlations[role.lower()]


def _extract_json_ids(info):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        'AUTHOR|(INSPIRE)': 'INSPIRE',
        'AUTHOR|(CDS)': 'CDS',
        '(SzGeCERN)': 'CERN'
    }
    regex = re.compile(r'((AUTHOR\|\((CDS|INSPIRE)\))|(\(SzGeCERN\)))(.*)')
    ids = []
    match = regex.match(info.get('0', ''))
    if match:
        ids.append({
            'value': match.group(5),
            'source': SOURCES[match.group(1)]
        })
    # Try and get the IDs from the auto-completion
    try:
        ids.append({'value': info['cernccid'], 'source': 'CERN'})
    except KeyError:
        pass
    try:
        ids.append({'value': info['recid'], 'source': 'CDS'})
    except KeyError:
        pass
    try:
        ids.append({'value': info['inspireid'], 'source': 'INSPIRE'})
    except KeyError:
        pass

    return ids


def build_contributor(value):
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
                contributor = build_contributor(
                    {'a': name.strip(), 'e': 'camera'})
                if contributor:
                    contributors.append(contributor[0])
            return contributors
    else:
        return build_contributor({'a': item.strip(), 'e': 'credits'})
