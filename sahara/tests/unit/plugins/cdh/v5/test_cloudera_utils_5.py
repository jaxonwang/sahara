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


    @mock.patch('uuid.uuid4')
    @mock.patch('sahara.conductor.API.cluster_update')
    @mock.patch('sahara.conductor.API.cluster_get')
    @mock.patch('sahara.plugins.cdh.cloudera_utils.api_client.ApiResource')
    def test_update_cloudera_password(self, ApiResource, cluster_get,
            cluster_update, uuid4):
        api = ApiResource()
        password = "9bcc0abe-766c-48f8-8b34-f5eac8ccc7fd"
        uuid4.return_value = password
        cluster = ctu.get_fake_cluster()
        cluster_get().extra = None
        self.CU.update_cloudera_password(cluster)
        self.assertEqual(password, api.get_user().password)
        api.update_user.assert_called_once_with(api.get_user())

    @mock.patch('sahara.conductor.API.cluster_update')
    @mock.patch('sahara.conductor.API.cluster_get')
    @mock.patch('sahara.plugins.cdh.cloudera_utils.api_client.ApiResource')
    def test_start_instances(self, ApiResource, cluster_get,
            cluster_update):
        api = ApiResource()
        cluster = ctu.get_fake_cluster()
        management_ip = cluster.node_groups[0].instances[0].management_ip
        self.CU.start_instances(cluster)
        ApiResource.assert_called_with(management_ip,
                                       username=self.CU.CM_DEFAULT_USERNAME,
                                       password=cluster_get().extra.get(),
                                       version=self.CU.CM_API_VERSION)
        api.get_cluster.assert_called_once_with(cluster.name)

    @mock.patch('sahara.config.CONF.disable_event_log')
    @mock.patch('sahara.conductor.API.cluster_update')
    @mock.patch('sahara.conductor.API.cluster_get')
    @mock.patch('sahara.plugins.cdh.cloudera_utils.api_client.ApiResource')
    def test_delete_instances(self, ApiResource, cluster_get,
            cluster_update, cfg):
        api = ApiResource()
        cluster = ctu.get_fake_cluster()
        # instances to be detete, with fqdn worker-1 to worker-3
        instances = [mock.Mock() for i in range(3)]
        for i, instance in enumerate(instances):
            instance.fqdn.return_value = 'worker-{0}'.format(i + 1)

        # all hosts, with fqdn worker-0 to worker-5
        hosts = [mock.Mock() for i in range(5)]
        for i, host in enumerate(hosts):
            host.hostname = 'worker-{0}'.format(i)
        api.get_all_hosts.return_value = hosts

        self.CU.delete_instances(cluster, instances)
        cm_cluster = api.get_cluster()

        calls = [mock.call(host.hostId) for host in hosts[1:4]] 
        cm_cluster.remove_host.assert_has_calls(calls)
        api.delete_host.assert_has_calls(calls)

    @mock.patch('sahara.config.CONF.disable_event_log')
    @mock.patch('sahara.conductor.API.cluster_update')
    @mock.patch('sahara.conductor.API.cluster_get')
    @mock.patch('sahara.plugins.cdh.cloudera_utils.api_client.ApiResource')
    def test_decomision_nodes(self, ApiResource, cluster_get,
            cluster_update, cfg):
        cluster = ctu.get_fake_cluster()

        role_names = ['DN_worker_00', 'DN_worker_01', 'DN_worker_02']
        self.CU.decommission_nodes(cluster, 'DATANODE', role_names)
        service = ApiResource().get_cluster().get_service()
        service.decommission.assert_called_with(*role_names)
        service.delete_role.assert_has_calls(map(mock.call, role_names))
