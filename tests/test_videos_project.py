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
import mock

from cds_dojson.marc21.fields.videos.utils import language_to_isocode
from cds_dojson.marc21.models.videos.project import model
from cds_dojson.marc21.utils import create_record
from helpers import load_fixture_file, mock_contributor_fetch, validate


def test_required_fields(app):
    """Test required fields."""
    marcxml = load_fixture_file('videos_project.xml')

    with app.app_context():
        with mock.patch(
            "cds_dojson.marc21.fields.utils.get_author_info_from_people_collection",
            side_effect=lambda contributor: mock_contributor_fetch(contributor),
        ):

            blob = create_record(marcxml)
            record = model.do(blob)

            assert record == {
                '$schema': {
                    '$ref': ('https://cds.cern.ch/schemas/'
                            'records/videos/project/project-v1.0.0.json')
                },
                '_access': {'update': ['another.user@cern.ch']},
                'category': 'CERN',
                'contributors': [
                    {'name': 'CERN Video Productions', 'role': 'Producer'},
                    {'name': 'CERN Video Productions', 'role': 'Director'}
                ],
                'keywords': [{'name': 'Higgs', 'source': 'CERN'},
                            {'name': 'anniversary', 'source': 'CERN'}],
                'recid': 2272969,
                'report_number': ['CERN-MOVIE-2017-023'],
                'title': {'title': 'Higgs anniversary 5Y'},
                'type': 'MOVIE',
                'videos': [{'$ref': 'https://cds.cern.ch/record/1'},
                        {'$ref': 'https://cds.cern.ch/record/2'}],
                'external_system_identifiers': [
                    {'schema': 'AVW', 'value': 'AVW.project.2963'}
                ],
                'modified_by': 'another.user@cern.ch',
            }

            # Add required fields calculated by post-process tasks.
            record['publication_date'] = '2017-07-04'
            record['date'] = '2017-07-04'
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
                '$ref': ('https://cds.cern.ch/schemas/'
                         'records/videos/project/project-v1.0.0.json')
            }
        }
        expected.update(**json_body)
        assert record == expected

    with app.app_context():
        with mock.patch(
            "cds_dojson.marc21.fields.utils.get_author_info_from_people_collection",
            side_effect=lambda contributor: mock_contributor_fetch(contributor),
        ):
            check_transformation(
                """
                <datafield tag="260" ind1=" " ind2=" ">
                    <subfield code="c">2005</subfield>
                </datafield>
                <datafield tag="269" ind1=" " ind2=" ">
                    <subfield code="c">2001-02-03</subfield>
                </datafield>
                """, {
                })
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
                    <subfield code="a">Camera Operator, Test User 2</subfield>
                </datafield>
                <datafield tag="508" ind1=" " ind2=" ">
                    <subfield code="a"> test2</subfield>
                </datafield>
                <datafield tag="508" ind1=" " ind2=" ">
                    <subfield code="a">Camera Operator</subfield>
                </datafield>
                <datafield tag="700" ind1=" " ind2=" ">
                    <subfield code="a">Test User</subfield>
                    <subfield code="e">Director</subfield>
                </datafield>
                """, {
                    'contributors': [
                        {'name': 'CERN Video Productions', 'role': 'Producer'},
                        {'name': 'CERN Video Productions', 'role': 'Director'},
                        {
                            'email': u'tuser2@cern.ch',
                            'ids': [{'source': 'CERN', 'value': u'9876542'},
                                    {'source': 'CDS', 'value': u'2123456789'}],
                            'name': 'User, Test 2', 'role': 'Camera Operator'
                        },
                        {'name': 'test2', 'role': 'Credits'},
                        {
                            'email': u'tuser@cern.ch',
                            'ids': [{'source': 'CERN', 'value': u'987654'},
                                    {'source': 'CDS', 'value': u'123456789'}],
                            'name': 'User, Test', 'role': 'Director'
                        },
                    ]
                })
            check_transformation(
                """
                <datafield tag="774" ind1=" " ind2=" ">
                    <subfield code="u">test1</subfield>
                </datafield>
                <datafield tag="774" ind1=" " ind2=" ">
                    <subfield code="u">test2</subfield>
                </datafield>
                """, {
                    'videos': [
                        {'$ref': 'test1'},
                        {'$ref': 'test2'},
                    ]
                })
            check_transformation(
                """
                <datafield tag="520" ind1=" " ind2=" ">
                    <subfield code="a">test1</subfield>
                </datafield>
                """, {
                    'description': 'test1',
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
                <datafield tag="970" ind1=" " ind2=" ">
                    <subfield code="a">000012345.MDD</subfield>
                </datafield>
                <datafield tag="970" ind1=" " ind2=" ">
                    <subfield code="a">FCS.project.2345</subfield>
                </datafield>
                """, {
                    'external_system_identifiers': [
                        {'value': '000012345.MDD', 'schema': 'ALEPH'},
                        {'value': 'FCS.project.2345', 'schema': 'FCS'}
                    ]
                })


def test_language_to_isocode():
    """Test language to isocode."""
    assert language_to_isocode('eng') == 'en'
    assert language_to_isocode('eng-fre') == 'en-fr'
    assert language_to_isocode('ITA') == 'it'
    assert language_to_isocode('silent') == 'silent'
    assert language_to_isocode('sil') == 'silent'
    assert language_to_isocode('fuu') == 'silent'
