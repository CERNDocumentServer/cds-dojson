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
# 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.
import pytest
from dojson.contrib import marc21 as default

from cds_dojson.marc21.models.books import book, journal, multipart, serial, standard
from cds_dojson.marc21.models.videos import project, video
from cds_dojson.matcher import matcher


def test_marc21_matcher_videos():
    """Test CDS DoJSON matcher - videos"""
    video_blob1 = {'980__': [{'a': 'PUBLVIDEOMOVIE'}, {'b': 'VIDEOMEDIALAB'}]}
    video_blob2 = {'980__': [{'a': 'PUBLVIDEOMOVIE'}, {'c': 'DELETED'}]}
    video_blob3 = {'980__': {'a': 'VIDEOARC'}}
    video_blob4 = {'980__': {'a': 'CERNVIDEOSHOOT'}}
    video_blob5 = {'980__': [{'a': 'PUBLVIDEOMOVIE'}, {'b': 'VIDEOMEDIALAB'}],
                   '970__': {'a': 'AVW.project.1234'}}
    video_blob6 = {'980__': [{'a': 'PUBLVIDEOMOVIE'}, {'c': 'DELETED'}],
                   '970__': {'a': 'AVW.project.1234'}}
    video_blob7 = {'970__': {'a': 'FCS.project.987'}}
    not_match = {'foo': 'bar'}

    assert video.model == matcher(video_blob1, 'cds_dojson.marc21.models')
    assert default.model == matcher(video_blob2, 'cds_dojson.marc21.models')
    assert default.model == matcher(video_blob3, 'cds_dojson.marc21.models')
    assert default.model == matcher(video_blob4, 'cds_dojson.marc21.models')
    assert project.model == matcher(video_blob5, 'cds_dojson.marc21.models')
    assert default.model == matcher(video_blob6, 'cds_dojson.marc21.models')
    assert project.model == matcher(video_blob7, 'cds_dojson.marc21.models')
    assert default.model == matcher(not_match, 'cds_dojson.marc21.models')


def test_marc21_matcher_books():
    """Test CDS DoJSON matcher - books."""
    book_blob1 = {'690C_': [{'a': 'BOOK'}]}
    book_blob2 = {'980__': [{'a': 'PROCEEDINGS'}]}
    book_blob3 = {'697C_': [{'a': 'ENGLISH BOOK CLUB'}]}
    serial_blob1 = {'690C_': [{'a': 'BOOK'}],
                    '490__': {'a': 'Test title'}}
    serial_blob2 = {'690C_': [{'a': 'BOOK'}]}
    multipart_blob1 = {
        '690C_': [{'a': 'BOOK'}],
        '245__': [{'a': 'Test '}],
        '596__': [{'a': 'MULTIVOLUMES'}],
        '246__': [{'p': 'Volume Title', 'n': '2'}]
    }
    multipart_blob2 = {
        '690C_': [{'a': 'BOOK'}],
        '245__': [{'a': 'Test '}],
        '246__': [{'n': '2'}],
        '596__': [{'a': 'MULTIVOLUMES'}],
    }
    standard_blob1 = {'690C_': [{'a': 'STANDARD'}]}
    journal_blob = {'980__': [{'a': 'PERI'}]}
    not_match = {'foo': 'bar'}

    assert book.model == matcher(book_blob1, 'cds_dojson.marc21.models')
    assert book.model == matcher(book_blob2, 'cds_dojson.marc21.models')

    with pytest.raises(AssertionError):
        # English book club should not be matched
        assert book.model == matcher(book_blob3, 'cds_dojson.marc21.models')
    assert standard.model == matcher(standard_blob1,
                                     'cds_dojson.marc21.models')
    assert serial.model == matcher(serial_blob1,
                                   'cds_dojson.marc21.parent_models'
                                   )
    assert multipart.model == matcher(multipart_blob1,
                                      'cds_dojson.marc21.parent_models')
    assert multipart.model == matcher(multipart_blob2,
                                      'cds_dojson.marc21.parent_models')
    assert journal.model == matcher(journal_blob,
                                    'cds_dojson.marc21.parent_models')
    # make sure that it won't match if 490 not there
    assert default.model == matcher(serial_blob2,
                                    'cds_dojson.marc21.parent_models'
                                    )
    assert default.model == matcher(not_match, 'cds_dojson.marc21.models')
