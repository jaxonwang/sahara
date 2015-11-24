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

from sahara.plugins.cdh import cloudera_utils as cu
from sahara.plugins import exceptions as ex
from sahara.tests.unit import base
from sahara.tests.unit.plugins.cdh import utils as ctu


class ClouderaUtilsTestCase(base.SaharaTestCase):

    def setUp(self):
        super(ClouderaUtilsTestCase, self).setUp()
        self.CU = cu.ClouderaUtils()

    def test_cloudera_cmd(self):
        def _get_function_yield(result_success=False,
                                result_children=None):
            cmd = mock.Mock()
            cmd.wait().success = result_success
            cmd.wait().children = result_children
            return cmd

        sucessful_cmd = _get_function_yield(result_success=True)
        failed_cmd = _get_function_yield(result_success=False)
        successful_child = mock.Mock()
        successful_child.success = True
        failed_child = mock.Mock()
        failed_child.success = False
        failed_cmd_with_children = _get_function_yield(
            result_success=False,
            result_children=[successful_child,
                             failed_child])

        function = mock.MagicMock(return_value=[sucessful_cmd])
        function.__name__ = "a_mock_function"  # needed for functools.wraps
        cu.cloudera_cmd(function)()  # should not raise
        function.return_value = [sucessful_cmd, failed_cmd]
        self.assertRaises(ex.HadoopProvisionError,
                          cu.cloudera_cmd(function))
        function.return_value = [failed_cmd_with_children]
        self.assertRaises(ex.HadoopProvisionError,
                          cu.cloudera_cmd(function))

    def test_get_service(self):
        self.CU.get_cloudera_cluster = mock.MagicMock(return_value = None)
        self.assertRaises(ValueError, self.CU.get_service_by_role, 'NAMENODE')

        cluster = ctu.get_fake_cluster()
        inst = cluster.node_groups[0].instances[0]
        self.CU.get_cloudera_cluster.return_value = None

        self.assertRaises(ValueError, self.CU.get_service_by_role, 'spam',
                          cluster)
        self.assertRaises(ValueError, self.CU.get_service_by_role, 'spam',
                          instance=inst)

        self.CU.get_cloudera_cluster.reset_mock()

        mock_get_service = mock.MagicMock()
        mock_get_service.get_service.return_value = mock.Mock()
        self.CU.get_cloudera_cluster.return_value = mock_get_service

        self.CU.get_service_by_role('NAMENODE', cluster)
        args = ((self.CU.HDFS_SERVICE_NAME,),)
        self.assertEqual(args, mock_get_service.get_service.call_args)

        mock_get_service.reset_mock()
        self.CU.get_service_by_role('JOBHISTORY', instance=inst)
        args = ((self.CU.YARN_SERVICE_NAME,),)
        self.assertEqual(args, mock_get_service.get_service.call_args)

        mock_get_service.reset_mock()
        self.CU.get_service_by_role('OOZIE_SERVER', cluster)
        args = ((self.CU.OOZIE_SERVICE_NAME,),)
        self.assertEqual(args, mock_get_service.get_service.call_args)

    def test_get_service_by_role(self):
        class Ob(object):

            def get_service(self, x):
                return x
        self.CU.get_cloudera_cluster = mock.MagicMock(return_value=Ob())
        roles = ['NAMENODE', 'DATANODE', 'SECONDARYNAMENODE', 'HDFS_GATEWAY',
                 'RESOURCEMANAGER', 'NODEMANAGER', 'JOBHISTORY',
                 'YARN_GATEWAY', 'OOZIE_SERVER', 'HIVESERVER2',
                 'HIVEMETASTORE', 'WEBHCAT', 'HUE_SERVER',
                 'SPARK_YARN_HISTORY_SERVER', 'SERVER', 'MASTER',
                 'REGIONSERVER']
        resps = ['hdfs01', 'hdfs01', 'hdfs01', 'hdfs01', 'yarn01', 'yarn01',
                 'yarn01', 'yarn01', 'oozie01', 'hive01', 'hive01', 'hive01',
                 'hue01', 'spark_on_yarn01', 'zookeeper01', 'hbase01',
                 'hbase01']
        cluster = mock.Mock()
        for (role, resp) in zip(roles, resps):
            self.assertEqual(
                resp, self.CU.get_service_by_role(role, cluster=cluster))

        with testtools.ExpectedException(ValueError):
            self.CU.get_service_by_role('cat', cluster=cluster)
