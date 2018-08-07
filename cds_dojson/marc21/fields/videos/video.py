# -*- coding: utf-8 -*-
#
# This file is part of CERN Document Server.
# Copyright (C) 2017, 2018 CERN.
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
"""Video fields."""

from __future__ import absolute_import, print_function

import os
import re
from collections import defaultdict
from copy import deepcopy

import arrow
from dojson.errors import IgnoreKey
from dojson.utils import (filter_values, for_each_value, force_list,
                          ignore_value)
from six import iteritems

from ...models.videos.video import model
from .utils import language_to_isocode

# Required fields


@model.over('duration', '^300__')
def duration(self, key, value):
    """Duration.

    The new duration must be expressed in the form hh:mm:ss[.mmm], if it isn't,
    i.e. '2 min.', we will extract it programatically later to avoid the hassle
    off dealing with more regex.
    """
    try:
        return re.match(r'(\d{2}:\d{2}:\d{2})(\.\d+)?', value.get('a')) \
            .group(1)
    except (AttributeError, TypeError):
        # The regex didn't match, we will extract the duration later.
        return '00:00:00'


# Language

@model.over('language', '^041__')
def language(self, key, value):
    """Language."""
    return language_to_isocode(value.get('a'))


# Rest

@model.over('physical_medium', '(^340__)|(^852__)')
def physical_medium(self, key, value):
    """Physical medium."""
    def find_match(seq, copy):
        if not seq and not copy \
                and key == '852__' and len(_physical_medium) == 1:
            return _physical_medium[0]
        else:
            for i in _physical_medium:
                if seq and seq in i.get('sequence_number') \
                        or copy and copy == i.get('copy_number'):
                    return i

        _physical_medium.append({})
        return _physical_medium[-1]

    _physical_medium = self.get('physical_medium', [])
    sequence_numbers = []
    for value in force_list(value):
        pm = find_match(value.get('8'), value.get('y'))
        # Append ``_8`` and ``_9``
        sequence_numbers.append(value.get('8'))
        sequence_numbers.append(value.get('9'))
        if key == '340__':
            pm.update({
                'medium_standard': value.get('a'),
                'note': value.get('j'),
                'camera': value.get('d'),
                'arrangement': value.get('k'),
                'copy_number': value.get('t'),
            })
        elif key == '852__':
            pm.update({
                'internal_note': value.get('9'),
                'location': value.get('a'),
                'shelf': value.get('b'),
                'bar_code': value.get('c'),
                'copy_number': value.get('t'),
                'note': value.get('z'),
            })
        pm.update({
            'sequence_number': [
                sequence_number for sequence_number in set(sequence_numbers)
                if sequence_number is not None
            ]
        })
    return [dict((k, v) for k, v in iteritems(i) if v is not None)
            for i in _physical_medium]


@model.over('_project_id', '^773__')
@ignore_value
def project_id(self, key, value):
    """Report number."""
    values = force_list(value)
    project_id = None
    related_links = self.get('related_links', [])
    for value in values:
        related_link = {}
        if 'p' in value and 'u' in value:
            related_link['name'] = value.get('p')
            related_link['url'] = value.get('u')
            related_links.append(related_link)
        else:
            project_id = value.get('u')
    if related_links:
        self['related_links'] = related_links
    if not project_id:
        raise IgnoreKey('project_id')
    return project_id


@model.over('location', '^110__')
def location(self, key, value):
    """Location."""
    return value.get('a')


@model.over('internal_note', '^595__')
@ignore_value
def internal_note(self, key, value):
    """Internal note."""
    CATEGS = ('CERN50', 'CERN EDS', 'Video-SR-F', 'Pilote PICTURAE', 'Press')
    _internal_categories = defaultdict(list)
    _internal_categories.update(self.get('internal_categories', {}))
    _internal_notes = self.get('internal_note', '').splitlines()
    for v in force_list(value):
        if v.get('a') in CATEGS:
            _internal_categories[v.get('a')].append(v.get('s'))
        else:
            _internal_notes.append(v.get('a'))

    if _internal_categories:
        self['internal_categories'] = dict(_internal_categories)
    return '\n'.join(_internal_notes) or None


@model.over('subject', '^65017')
def subject(self, key, value):
    """Subject."""
    return {
        'source': value.get('2', 'SzGeCERN'),
        'term': value.get('a')
    }


@model.over('accelerator_experiment', '^693__')
@filter_values
def accelerator_experiment(self, key, value):
    """Accelerator experiments."""
    return {
        'accelerator': value.get('a'),
        'experiment': value.get('e'),
        'study': value.get('s'),
        'facility': value.get('f'),
        'project': value.get('p'),
    }


@model.over('date', '^269__')
def date(self, key, value):
    """Date."""
    return arrow.get(value.get('c')).strftime('%Y-%m-%d')


@model.over('copyright', '^542__')
@filter_values
def copyright(self, key, value):
    """Copyright."""
    return {
        'holder': value.get('d'),
        'year': value.get('g'),
        'message': value.get('f'),
    }


@model.over('_files', '^8567_')
@for_each_value
@filter_values
def _files(self, key, value):
    """File list."""
    def get_key(value):
        if value.get('d'):
            return value.get('d').split('\\')[-1]
        else:
            return os.path.basename(value.get('u'))

    def get_context_type(value):
        if value.get('d'):
            return 'master', 'video'
        if value.get('y').startswith('thumbnail'):
            return 'ignore', 'ignore'
        if value.get('x').startswith('wmv'):
            return 'ignore', 'ignore'
        if value.get('x').startswith('flv'):
            return 'ignore', 'ignore'
        if 'kbps maxH' in value.get('y'):
            return 'subformat', 'video'
        if value.get('x') == 'subtitle':
            return 'playlist', 'text'
        if value.get('y').startswith('posterframe'):
            if ' 5 percent' in value.get('y'):
                return 'poster', 'image'
            else:
                return 'frame', 'image'
        return None, None

    def get_tags(context_type, value):
        if context_type == 'poster':
            wh = value.get('y').split(' ')[1]
            [width, height] = wh.split('x')
            return {'width': width, 'height': height}
        if value.get('x') == 'subtitle':
            return {
                'language': language_to_isocode(
                    value.get('y').split(' ')[1][:3])
            }
        if context_type == 'master':
            return {'preview': True}
        return {}

    def get_filepath(value):
        if value.get('d'):
            return value.get('d')[
                len('\\\\cern.ch\\dfs\\Services\\'):
            ].replace('\\', '/')
        else:
            return re.sub(
                'https?://mediaarchive.cern.ch/', '', value.get('u', '')
            )

    def get_tags_to_guess_preset(context_type, value):
        info = value.get('y').split(' ')
        return {
            'video_bitrate': int(info[0]),
            'preset': '{0}p'.format(info[3])
        }

    def get_tags_to_transform(context_type, value):
        if context_type in ['frame', 'poster']:
            return {'timestamp': int(value.get('y').split(' ')[3])}

    def get_frame_name(result):
        _, ext = os.path.splitext(result['key'])
        index = (int(result['tags_to_transform']['timestamp']) // 10) + 1
        return "frame-{0}{1}".format(index, ext)

    # ignore 'x' sometimes (when is not useful)
    value.get('x')

    def compute(value, context_type, media_type):
        result = {}
        result['key'] = get_key(value)
        result['tags'] = get_tags(context_type, value)
        result['tags'].update(context_type=context_type, media_type=media_type)
        result['tags']['content_type'] = os.path.splitext(result['key'])[1][1:]
        result['filepath'] = get_filepath(value)
        if context_type == 'subformat':
            result['tags_to_guess_preset'] = get_tags_to_guess_preset(
                context_type, value)
        result['tags_to_transform'] = get_tags_to_transform(
            context_type, value)

        if result['key'].startswith('proxy-') or context_type == 'ignore':
            # skip proxy files
            raise IgnoreKey('_files')

        if context_type == 'frame':
            # update key name
            result['key'] = get_frame_name(result)

        return result

    result = compute(deepcopy(value), *get_context_type(value))

    # if it's the poster frame, make a copy for a frame!
    if result['tags']['context_type'] == 'poster' and \
            result['tags_to_transform']['timestamp'] == 5:
        frame_5 = compute(value, 'frame', 'image')
        if '_files' not in self:
            self['_files'] = []
        self['_files'].append(frame_5)
        # update posterframe key name
        _, ext = os.path.splitext(result['key'])
        result['key'] = 'posterframe{0}'.format(ext)

    return result


@model.over('audio_characteristics', '^344__')
def audio_characteristics(self, key, value):
    """Audio characteristics."""
    return {
        'playback_channels': value.get('g'),
    }
