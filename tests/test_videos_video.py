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
"""Video rules tests."""

from cds_dojson.marc21.fields.videos.utils import language_to_isocode
from cds_dojson.marc21.models.videos.video import model
from cds_dojson.marc21.utils import create_record
from helpers import load_fixture_file, validate


def test_required_fields(app):
    """Test required fields."""
    marcxml = load_fixture_file('videos_video.xml')

    with app.app_context():
        blob = create_record(marcxml)
        record = model.do(blob)

        assert record == {
            '$schema': {
                '$ref': ('https://cds.cern.ch/schemas/records/videos/video/'
                         'video-v1.0.0.json')
            },
            '_access': {'read': ['test-group@cern.ch',
                                 'cds-admin@cern.ch',
                                 'test-email@cern.ch',
                                 'example@test.com'],
                        'update': ['Jacques.Fichet@cern.ch',
                                   'christoph.martin.madsen@cern.ch']},
            '_files': [
                {
                    'filepath': 'MediaArchive/Video/Masters/Movies/CERN/2017/CERN-MOVIE-2017-023/Final_Output/CERN-MOVIE-2017-023-001.mov',
                    'key': 'CERN-MOVIE-2017-023-001.mov',
                    'tags': {
                        'media_type': 'video',
                        'content_type': 'mov',
                        'context_type': 'master',
                    },
                },
                {
                    'filepath': 'MediaArchive/Video/Public/Movies/CERN/2017/CERN-MOVIE-2017-023/CERN-MOVIE-2017-023-001/CERN-MOVIE-2017-023-001-5872-kbps-1920x1080-audio-128-kbps-stereo.mp4',
                    'key': 'CERN-MOVIE-2017-023-001-5872-kbps-1920x1080-audio-128-kbps-stereo.mp4',
                    'tags_to_guess_preset': {'preset': '1080p', 'video_bitrate': 5872},
                    'tags': {
                        'media_type': 'video',
                        'content_type': 'mp4',
                        'context_type': 'subformat',
                    },
                },
                {
                    'filepath': 'MediaArchive/Video/Public/Movies/CERN/2017/CERN-MOVIE-2017-023/CERN-MOVIE-2017-023-001/CERN-MOVIE-2017-023-001-2672-kbps-1280x720-audio-128-kbps-stereo.mp4',
                    'key': 'CERN-MOVIE-2017-023-001-2672-kbps-1280x720-audio-128-kbps-stereo.mp4',
                    'tags_to_guess_preset': {'preset': '720p', 'video_bitrate': 2672},
                    'tags': {
                        'media_type': 'video',
                        'content_type': 'mp4',
                        'context_type': 'subformat',
                    },
                },
                {
                    'filepath': 'MediaArchive/Video/Public/Movies/CERN/2017/CERN-MOVIE-2017-023/CERN-MOVIE-2017-023-001/CERN-MOVIE-2017-023-001-1436-kbps-853x480-audio-64-kbps-stereo.mp4',
                    'key': 'CERN-MOVIE-2017-023-001-1436-kbps-853x480-audio-64-kbps-stereo.mp4',
                    'tags_to_guess_preset': {'preset': '480p', 'video_bitrate': 1436},
                    'tags': {
                        'media_type': 'video',
                        'content_type': 'mp4',
                        'context_type': 'subformat',
                    },
                },
                {
                    'filepath': 'MediaArchive/Video/Public/Movies/CERN/2017/CERN-MOVIE-2017-023/CERN-MOVIE-2017-023-001/CERN-MOVIE-2017-023-001-836-kbps-640x360-audio-64-kbps-stereo.mp4',
                    'key': 'CERN-MOVIE-2017-023-001-836-kbps-640x360-audio-64-kbps-stereo.mp4',
                    'tags_to_guess_preset': {'preset': '360p', 'video_bitrate': 836},
                    'tags': {
                        'media_type': 'video',
                        'content_type': 'mp4',
                        'context_type': 'subformat',
                    },
                },
                {
                    'filepath': 'MediaArchive/Video/Public/Movies/CERN/2017/CERN-MOVIE-2017-023/CERN-MOVIE-2017-023-001/CERN-MOVIE-2017-023-001-386-kbps-426x240-audio-64-kbps-stereo.mp4',
                    'key': 'CERN-MOVIE-2017-023-001-386-kbps-426x240-audio-64-kbps-stereo.mp4',
                    'tags_to_guess_preset': {'preset': '240p', 'video_bitrate': 386},
                    'tags': {
                        'media_type': 'video',
                        'content_type': 'mp4',
                        'context_type': 'subformat',
                    },
                },
                {
                    'filepath': 'MediaArchive/Video/Public/Movies/CERN/2017/CERN-MOVIE-2017-023/CERN-MOVIE-2017-023-001/CERN-MOVIE-2017-023-001-posterframe-640x360-at-5-percent.jpg',
                    'key': 'CERN-MOVIE-2017-023-001-posterframe-640x360-at-5-percent.jpg',
                    'tags': {
                        'media_type': 'image',
                        'height': '360',
                        'width': '640',
                        'content_type': 'jpg',
                        'context_type': 'poster',
                    }
                }
            ],
            '_project_id': 'CERN-MOVIE-2017-023',
            'category': 'CERN',
            'contributors': [
                {'name': 'CERN Video Productions', 'role': 'Producer'},
                {'name': 'CERN Video Productions', 'role': 'Director'},
                {'affiliations': (u'CERN',),
                 'email': u'christoph.martin.madsen@cern.ch',
                 'ids': [{'source': 'CERN', 'value': u'755568'},
                         {'source': 'CDS', 'value': u'2090563'}],
                 'name': 'Madsen, Christoph Martin',
                 'role': 'Director'},
                {'affiliations': (u'CERN',),
                 'email': u'Paola.Catapano@cern.ch',
                 'ids': [{'source': 'CERN', 'value': u'380837'},
                         {'source': 'CDS', 'value': u'2050975'}],
                 'name': 'Catapano, Paola',
                 'role': 'Director'},
                {'affiliations': (u'CERN',),
                 'email': u'christoph.martin.madsen@cern.ch',
                 'ids': [{'source': 'CERN', 'value': u'755568'},
                         {'source': 'CDS', 'value': u'2090563'}],
                 'name': 'Madsen, Christoph Martin',
                 'role': 'Editor'}],
            'copyright': {'holder': 'CERN', 'year': '2017'},
            'date': '2017-07-04',
            'description': ('Where were you on 4 July 2012, the day in which '
                            'the Higgs boson discovery was announced?'),
            'duration': '00:01:09',
            'keywords': [
                {'name': 'higgs', 'source': 'CERN'},
                {'name': 'anniversary', 'source': 'CERN'}
            ],
            'language': u'en',
            'recid': 2272973,
            'report_number': ['CERN-MOVIE-2017-023-001'],
            'title': {'title': 'Happy 5th anniversary, Higgs boson!'},
            'type': 'MOVIE',
            'external_system_identifiers': [
                {'schema': 'AVW', 'value': 'AVW.clip.3447'}
            ],
            'modified_by': 'Jacques.Fichet@cern.ch',
        }

        # Add required fields calculated by post-process tasks.
        record['publication_date'] = '2017-07-04'
        record['doi'] = 'CERN/2272973'
        record['license'] = [
            {'license': 'CC BY 4.0',
             'url': 'https://creativecommons.org/licenses/by/4.0/'}
        ]
        validate(record)


def test_fields(app):
    """Test fields."""
    marcxml = ("""<collection xmlns="http://www.loc.gov/MARC21/slim">"""
               """<record>{0}</record></collection>""")

    def check_transformation(marcxml_body, json_body):
        blob = create_record(marcxml.format(marcxml_body))
        record = model.do(blob)
        expected = {
            '$schema': {
                '$ref': ('https://cds.cern.ch/schemas/records/videos/video/'
                         'video-v1.0.0.json')
            }
        }
        expected.update(**json_body)
        assert record == expected

    with app.app_context():
        check_transformation(
            """
            <datafield tag="541" ind1=" " ind2=" ">
                <subfield code="e">test1</subfield>
            </datafield>
            """, {
                'original_source': 'test1',
            })
        check_transformation(
            """
            <datafield tag="590" ind1="4" ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            """, {
                'note': 'test1',
            })
        check_transformation(
            """
            <datafield tag="500" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            """, {
                'note': 'test1',
            })
        check_transformation(
            """
            <datafield tag="269" ind1=" " ind2=" ">
                <subfield code="c">2017-03-15</subfield>
            </datafield>
            """, {
                'date': '2017-03-15',
            })
        check_transformation(
            """
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="a">test1A</subfield>
                <subfield code="d">test2A</subfield>
            </datafield>
            <datafield tag="852" ind1=" " ind2=" ">
                <subfield code="a">loc_test1A</subfield>
            </datafield>
            """, {
                'physical_medium': [
                    {
                        'camera': 'test2A',
                        'medium_standard': 'test1A',
                        'location': 'loc_test1A'
                    }
                ]
            })
        check_transformation(
            """
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="8">A</subfield>
                <subfield code="a">test1A</subfield>
                <subfield code="d">test2A</subfield>
            </datafield>
            <datafield tag="340" ind1=" " ind2=" ">
                <subfield code="8">B</subfield>
                <subfield code="a">test1B</subfield>
                <subfield code="d">test2B</subfield>
            </datafield>
            <datafield tag="852" ind1=" " ind2=" ">
                <subfield code="8">B</subfield>
                <subfield code="a">loc_test1B</subfield>
            </datafield>
            <datafield tag="852" ind1=" " ind2=" ">
                <subfield code="8">A</subfield>
                <subfield code="a">loc_test1A</subfield>
            </datafield>
            """, {
                'physical_medium': [
                    {
                        'sequence_number': 'A',
                        'camera': 'test2A',
                        'medium_standard': 'test1A',
                        'location': 'loc_test1A'
                    },
                    {
                        'sequence_number': 'B',
                        'camera': 'test2B',
                        'medium_standard': 'test1B',
                        'location': 'loc_test1B'
                    }
                ]
            })
        check_transformation(
            """
            <datafield tag="590" ind1="4" ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            """, {'note': 'test1'})
        check_transformation(
            """
            <datafield tag="540" ind1=" " ind2=" ">
                <subfield code="3">test1</subfield>
                <subfield code="u">test2</subfield>
                <subfield code="a">test3</subfield>
            </datafield>
            """, {
                'license': [
                    {'material': 'test1', 'url': 'test2', 'license': 'test3'}
                ],
            })
        check_transformation(
            """
            <datafield tag="542" ind1=" " ind2=" ">
                <subfield code="d">test1</subfield>
                <subfield code="g">test2</subfield>
                <subfield code="f">test3</subfield>
            </datafield>
            """, {
                'copyright': {
                    'holder': 'test1', 'year': 'test2', 'message': 'test3'
                },
            })
        check_transformation(
            """
            <datafield tag="653" ind1="1" ind2=" ">
                <subfield code="a">test1</subfield>
                <subfield code="9">test2</subfield>
            </datafield>
            """, {
                'keywords': [
                    {'name': 'test1', 'source': 'test2'}
                ],
            })
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="r">test1</subfield>
            </datafield>
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="p">test1</subfield>
                <subfield code="u">test2</subfield>
            </datafield>
            """, {
                '_project_id': 'test1',
                'related_links': [
                    {'name': 'test1', 'url': 'test2'}
                ],
            })
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="r">test1</subfield>
            </datafield>
            """, {
                '_project_id': 'test1',
            })
        check_transformation(
            """
            <datafield tag="773" ind1=" " ind2=" ">
                <subfield code="p">test1</subfield>
                <subfield code="u">test2</subfield>
            </datafield>
            """, {
                'related_links': [
                    {'name': 'test1', 'url': 'test2'}
                ],
            })
        check_transformation(
            """
            <datafield tag="110" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            """, {
                'location': 'test1'
            })
        check_transformation(
            """
            <datafield tag="246" ind1=" " ind2="1">
                <subfield code="a">test1</subfield>
            </datafield>
            <datafield tag="590" ind1=" " ind2=" ">
                <subfield code="a">test2</subfield>
            </datafield>
            """, {
                'translations': [{
                    'title': {'title': 'test1'},
                    'description': 'test2',
                    'language': 'fr',
                }]
            })
        check_transformation(
            """
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            <datafield tag="590" ind1=" " ind2=" ">
                <subfield code="a">test2</subfield>
            </datafield>
            """, {
                'translations': [{
                    'title': {'title': 'test1'},
                    'description': 'test2',
                    'language': 'fr',
                }]
            })
        check_transformation(
            """
            <datafield tag="246" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            """, {
                'translations': [{
                    'title': {'title': 'test1'},
                    'language': 'fr',
                }]
            })
        check_transformation(
            """
            <datafield tag="590" ind1=" " ind2=" ">
                <subfield code="a">test2</subfield>
            </datafield>
            """, {
                'translations': [{
                    'description': 'test2',
                    'language': 'fr',
                }]
            })
        check_transformation(
            """
            <datafield tag="100" ind1=" " ind2=" ">
                <subfield code="a">CERN video productions</subfield>
                <subfield code="e">Produced by</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">CERN video productions</subfield>
                <subfield code="e">Director</subfield>
            </datafield>
            <datafield tag="508" ind1=" " ind2=" ">
                <subfield code="a">Camera Operator, Paola Catapano</subfield>
            </datafield>
            <datafield tag="508" ind1=" " ind2=" ">
                <subfield code="a"> test2</subfield>
            </datafield>
            <datafield tag="508" ind1=" " ind2=" ">
                <subfield code="a">Camera Operator</subfield>
            </datafield>
            <datafield tag="700" ind1=" " ind2=" ">
                <subfield code="a">Christoph Madsen</subfield>
                <subfield code="e">Director</subfield>
            </datafield>
            """, {
                'contributors': [
                    {'name': 'CERN Video Productions', 'role': 'Producer'},
                    {'name': 'CERN Video Productions', 'role': 'Director'},
                    {
                        'affiliations': (u'CERN',),
                        'email': u'Paola.Catapano@cern.ch',
                        'ids': [{'source': 'CERN', 'value': u'380837'},
                                {'source': 'CDS', 'value': u'2050975'}],
                        'name': 'Catapano, Paola',
                        'role': 'Camera Operator'
                    },
                    {'name': 'test2', 'role': 'Credits'},
                    {
                        'affiliations': (u'CERN',),
                        'email': u'christoph.martin.madsen@cern.ch',
                        'ids': [{'source': 'CERN', 'value': u'755568'},
                                {'source': 'CDS', 'value': u'2090563'}],
                        'name': 'Madsen, Christoph Martin', 'role': 'Director'
                    },
                ]
            })
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
                <subfield code="s">test2</subfield>
            </datafield>
            """, {'internal_note': 'test1, test2'}
        )
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="s">test2</subfield>
            </datafield>
            """, {'internal_note': 'test2'}
        )
        check_transformation(
            """
            <datafield tag="595" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
            </datafield>
            """, {'internal_note': 'test1'}
        )
        check_transformation(
            """
            <datafield tag="650" ind1="1" ind2="7">
                <subfield code="a">test1</subfield>
                <subfield code="2">test2</subfield>
            </datafield>
            <datafield tag="650" ind1=" " ind2=" ">
                <subfield code="a">test3</subfield>
                <subfield code="2">test4</subfield>
            </datafield>
            """, {
                'subject': {
                    'source': 'test2',
                    'term': 'test1',
                }
            })
        check_transformation(
            """
            <datafield tag="693" ind1=" " ind2=" ">
                <subfield code="a">test1</subfield>
                <subfield code="e">test2</subfield>
                <subfield code="s">test3</subfield>
                <subfield code="f">test4</subfield>
                <subfield code="p">test5</subfield>
            </datafield>
            """, {
                'accelerator_experiment': {
                    'accelerator': 'test1',
                    'experiment': 'test2',
                    'study': 'test3',
                    'facility': 'test4',
                    'project': 'test5',
                }
            }
        )


def test_language_to_isocode():
    """Test language to isocode."""
    assert language_to_isocode('eng') == 'en'
    assert language_to_isocode('eng-fre') == 'en-fr'
    assert language_to_isocode('ITA') == 'it'
    assert language_to_isocode('silent') == 'silent'
    assert language_to_isocode('sil') == 'silent'
    assert language_to_isocode('fuu') == 'silent'
    assert language_to_isocode('French') == 'fr'
