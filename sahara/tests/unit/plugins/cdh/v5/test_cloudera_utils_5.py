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



class ClouderaUtilsV5TestCase(cu.ClouderaUtilsTestCase):

    def setUp(self):
        self.CU = cu.ClouderaUtilsV5()

    @mock.patch('sahara.plugins.cdh.cloudera_utils.api_client.ApiResource')
    def test_get_api_client_by_default_password(self, ApiResource):
        cluster = ctu.get_fake_cluster()
        CU.get_api_client_by_default_password(cluster)
        CU.pu.get_manager.assert_called_with(cluster)
        management_ip = CU.pu.get_manager(cluster).management_ip
        ApiResource.assert_called_with(management_ip,
                                       username=CU.CM_DEFAULT_USERNAME,
                                       password=CU.CM_DEFAULT_PASSWD,
                                       version=CU.CM_API_VERSION)

