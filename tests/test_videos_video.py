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

from cds_dojson.marc21.models.videos.video import model
from cds_dojson.marc21.utils import create_record
from helpers import load_fixture_file, validate


def test_required_fields(app):
    """Test required fields."""
    marcxml = load_fixture_file('videos_video.xml')

    with app.app_context():
        blob = create_record(marcxml)
        record = model.do(blob)

        assert record['$schema'] == {
            '$ref': 'https://cds.cern.ch/schemas/records/videos/video/video-v1.0.0.json'
        }
        assert record['recid'] == 2272973
        assert record['date'] == '2017-07-04'
        assert record['duration'] == '00:01:09'
        assert record['title'][
            'title'] == 'Happy 5th anniversary, Higgs boson!'
        assert record['contributors'][0] == {
            'name': u'CERN Video Productions',
            'role': 'Producer'
        }
        assert record['contributors'][-1] == {
            'affiliations': ('CERN', ),
            'email': 'christoph.martin.madsen@cern.ch',
            'ids': [
                {'source': 'CERN', 'value': u'755568'},
                {'source': 'CDS', 'value': u'2090563'}
            ],
            'name': 'Madsen, Christoph Martin',
            'role': 'Editor'
        }
        assert record['_access'] == {
            'read': [
                'test-group@cern.ch',
                'cds-admin@cern.ch',
                'test-email@cern.ch',
                'example@test.com',
            ],
            'update': [
                'Jacques.Fichet@cern.ch',
                'christoph.martin.madsen@cern.ch',
            ]
        }

        # Add required fields calculated by post-process tasks.
        record['publication_date'] = '2017-07-04'
        validate(record)
