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

from dojson.contrib import marc21 as default

from cds_dojson.marc21.models.videos import project, video
from cds_dojson.matcher import matcher


def test_marc21_matcher():
    """Test CDS DoJSON matcher."""
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
