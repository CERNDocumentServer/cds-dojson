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
"""Video utils."""

import re
import pycountry

from dojson.utils import force_list
from six import iteritems

from ..utils import get_author_info_from_people_collection


def _get_correct_video_contributor_role(role):
    """Clean up roles."""
    tranlations = {
        '3d animation': 'Animatons by',
        '3d animations': 'Animations by',
        'animation': 'Animations by',
        'animations': 'Animations by',
        'auteur-r\xc3\xa9alisateur': ('Creator', 'Producer'),
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
        'enqu\xc3\xaate': 'Reporter',
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
        'redaktion': 'Editor',
        'related by': 'Narrator',
        'reporter': 'Reporter',
        'reports': 'Reporter',
        'r\xc3\xa9alisation': 'Producer',
        'scenario et realisation': 'Producer',
        'script': 'Screenwriter',
        'script & director': ('Screenwriter', 'Director'),
        'script and director': ('Screenwriter', 'Director'),
        'script, design and direction': ('Screenwriter', 'Editor', 'Director'),
        'sc\xc3\xa9nario et r\xc3\xa9alisation': 'Producer',
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
    return tranlations.get(role.lower())


def _extract_json_ids(info):
    """Extract author IDs from MARC tags."""
    SOURCES = {
        'AUTHOR|(INSPIRE)': 'INSPIRE',
        'AUTHOR|(CDS)': 'CDS',
        '(SzGeCERN)': 'CERN'
    }
    regex = re.compile('((AUTHOR\|\((CDS|INSPIRE)\))|(\(SzGeCERN\)))(.*)')
    ids = []
    for id_ in info.get('0', []):
        match = regex.match(id_)
        if not match:
            pass
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
    """Create a."""
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
    if value.get('a').lower() not in OLD_VIDEO_TEAM_NAMES:
        # Avoids a few calls
        value = get_author_info_from_people_collection(value)

    roles = force_list(_get_correct_video_contributor_role(value.get('e')))
    contributor = {
        'ids': _extract_json_ids(value) or None,
        'name': value.get('name') or value.get('a'),
        'affiliations': force_list(value.get('affiliation') or value.get('u')),
        'email': value.get('email'),
    }
    if contributor['name'].lower() in OLD_VIDEO_TEAM_NAMES:
        contributor['name'] = 'CERN Video Productions'

    contributors = []
    for r in roles:
        contributor['role'] = r
        contributors.append(
            dict((k, v) for k, v in iteritems(contributor) if v is not None))
    return contributors


def language_to_isocode(lang):
    """Translate language to isocode."""
    lang = lang.lower()
    try:
        return pycountry.languages.get(alpha_3=lang).alpha_2
    except (KeyError, AttributeError):
        exceptions = {
            'eng-fre': 'en-fr',
            'silent': 'silent',
            'sil': 'silent',
        }
        return exceptions.get(lang)
