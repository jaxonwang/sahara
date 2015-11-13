# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import six

from sahara.plugins.cdh import versionfactory as vf
from sahara.plugins.cdh import abstractversionhandler as avh
from sahara.tests.unit import base
from sahara.tests.unit.plugins.cdh import utils as ctu


class VersionFactoryTestCase(base.SaharaTestCase):

    def test_get_instance(self):
        self.assertFalse(vf.VersionFactory.initialized)
        factory = vf.VersionFactory.get_instance()
        self.assertTrue(isinstance(factory, vf.VersionFactory))
        self.assertTrue(vf.VersionFactory.initialized)

    def test_get_versions(self):
        factory = vf.VersionFactory.get_instance()
        versions = factory.get_versions()
        expect_versions = ctu.get_support_versions()
        self.assertEqual(versions, expect_versions)

    def test_get_version_handler(self):
        factory = vf.VersionFactory.get_instance()
        versions = ctu.get_support_versions()
        for version in versions:
            hander = factory.get_version_handler(version)
            self.assertTrue(isinstance(hander, avh.AbstractVersionHandler))
