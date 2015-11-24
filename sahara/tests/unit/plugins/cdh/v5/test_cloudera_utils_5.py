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

import mock
import testtools

from sahara.plugins.cdh.v5 import cloudera_utils as cu
from sahara.tests.unit import base
from sahara.tests.unit.plugins.cdh import utils as ctu
from sahara.tests.unit.plugins.cdh import test_cloudera_utils as tcu



class ClouderaUtilsV5TestCase(tcu.ClouderaUtilsTestCase):

    def setUp(self):
        super(ClouderaUtilsV5TestCase, self).setUp()
        self.CU = cu.ClouderaUtilsV5()

    @mock.patch('sahara.plugins.cdh.cloudera_utils.api_client.ApiResource')
    def test_get_api_client_by_default_password(self, ApiResource):
        cluster = ctu.get_fake_cluster()
        self.CU.get_api_client_by_default_password(cluster)
        management_ip = cluster.node_groups[0].instances[0].management_ip
        ApiResource.assert_called_with(management_ip,
                                       username=self.CU.CM_DEFAULT_USERNAME,
                                       password=self.CU.CM_DEFAULT_PASSWD,
                                       version=self.CU.CM_API_VERSION)

