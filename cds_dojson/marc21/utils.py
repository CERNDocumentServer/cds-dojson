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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Utilities for converting MARC21."""

from dojson.contrib.marc21.utils import MARC21_DTD, split_stream
from lxml import etree
from six import StringIO, binary_type, text_type
import copy

from ..utils import MementoDict


def create_record(marcxml, correct=False, keep_singletons=True):
    """Create a record object using the LXML parser.

    If correct == 1, then perform DTD validation
    If correct == 0, then do not perform DTD validation
    """
    if isinstance(marcxml, binary_type):
        marcxml = marcxml.decode('utf-8')

    if isinstance(marcxml, text_type):
        parser = etree.XMLParser(dtd_validation=correct, recover=True)

        if correct:
            marcxml = (u'<?xml version="1.0" encoding="UTF-8"?>\n'
                       u'<!DOCTYPE collection SYSTEM "file://{0}">\n'
                       u'<collection>\n{1}\n</collection>'.format(
                           MARC21_DTD, marcxml))

        tree = etree.parse(StringIO(marcxml), parser)
    else:
        tree = marcxml
    record = []

    leader_iterator = tree.iter(tag='{*}leader')
    for leader in leader_iterator:
        text = leader.text or ''
        record.append(('leader', text))

    controlfield_iterator = tree.iter(tag='{*}controlfield')
    for index, controlfield in enumerate(controlfield_iterator):
        tag = controlfield.attrib.get('tag', '!')
        text = controlfield.text or ''
        if text or keep_singletons:
            record.append((tag, text))

    multi_video = set()
    datafield_iterator = tree.iter(tag='{*}datafield')
    for datafield in datafield_iterator:
        tag = datafield.attrib.get('tag', '!')
        ind1 = datafield.attrib.get('ind1', '!')
        ind2 = datafield.attrib.get('ind2', '!')
        if ind1 in ('', '#'):
            ind1 = '_'
        if ind2 in ('', '#'):
            ind2 = '_'
        ind1 = ind1.replace(' ', '_')
        ind2 = ind2.replace(' ', '_')

        multi_video_with_index = False
        fields = []
        subfield_iterator = datafield.iter(tag='{*}subfield')
        for subfield in subfield_iterator:
            code = subfield.attrib.get('code', '!')  # .encode("UTF-8")
            text = subfield.text or ''
            if text or keep_singletons:
                fields.append((code, text))

                # Getting video indexes to create multiple records
                if tag == '856' and code == '8':
                    multi_video_with_index = True
                    multi_video = multi_video.union({text})

        # Handle the not indexed video
        if not multi_video_with_index:
            multi_video = multi_video.union({'not_indexed'})

        if fields or keep_singletons:
            key = '{0}{1}{2}'.format(tag, ind1, ind2)
            record.append((key, MementoDict(fields)))

    # Creating multiple records
    tags_indexes = {video: {} for video in multi_video}
    tags_counter = {video: 0 for video in multi_video}
    multi_video_dict = {video: [] for video in multi_video}
    for tag in record:
        # Tags with no code or with codes, but no '8' code
        if type(tag[1]) is not MementoDict or '8' not in tag[1].keys():
            for video in multi_video:
                multi_video_dict[video].append(copy.deepcopy(tag))
                
                if not(tag[0] in tags_indexes[video]):
                    tags_indexes[video][tag[0]] = tags_counter[video]

                tags_counter[video] += 1
                    

        # Tags with code '8'
        else:
            # Code 8 within the indexes of videos
            try:
                multi_video_dict[tag[1]['8']].append(copy.deepcopy(tag))

                if not(tag[0] in tags_indexes[tag[1]['8']]):
                    tags_indexes[tag[1]['8']][tag[0]] = tags_counter[tag[1]['8']]
                tags_counter[tag[1]['8']] += 1

            # Wrong code 8
            except:
                for video in multi_video:
                    multi_video_dict[video].append(copy.deepcopy(tag))
                    
                    if not(tag[0] in tags_indexes[video]):
                        tags_indexes[video][tag[0]] = tags_counter[video]

                    tags_counter[video] += 1
            
    # Removing redundant tags.
    # Always use as (tag_to_be_removed, tag_to_be_mantained)
    redundant_tags = [
        ('260__', '269__')
    ]
    
    for redundant in redundant_tags:
        for video in multi_video:
            if tags_indexes[video].get(redundant[0]) is not None and tags_indexes[video].get(redundant[1]) is not None:
                
                index_to_remove = tags_indexes[video][redundant[0]]
                while multi_video_dict[video][index_to_remove][0] == redundant[0]:
                    multi_video_dict[video].pop(tags_indexes[video][redundant[0]])

    if len(multi_video_dict.keys()) == 1:
        return MementoDict(multi_video_dict['not_indexed'])
    
    return [MementoDict(video_record) for video_record in multi_video_dict.values()]


def load(source):
    """Load MARC XML and return Python dict."""
    for data in split_stream(source):
        yield create_record(data)
