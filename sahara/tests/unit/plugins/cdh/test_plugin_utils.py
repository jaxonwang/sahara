# Copyright (c) 2015 Mirantis Inc.
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

from sahara.plugins.cdh import plugin_utils as pu
from sahara.tests.unit import base as b
from sahara.tests.unit.plugins.cdh import utils as ctu

CONFIGURATION_SCHEMA = {
    'node_configs': {
        'yarn.scheduler.minimum-allocation-mb': (
            'RESOURCEMANAGER', 'yarn_scheduler_minimum_allocation_mb'),
        'mapreduce.reduce.memory.mb': (
            'YARN_GATEWAY', 'mapreduce_reduce_memory_mb'),
        'mapreduce.map.memory.mb': (
            'YARN_GATEWAY', 'mapreduce_map_memory_mb',),
        'yarn.scheduler.maximum-allocation-mb': (
            'RESOURCEMANAGER', 'yarn_scheduler_maximum_allocation_mb'),
        'yarn.app.mapreduce.am.command-opts': (
            'YARN_GATEWAY', 'yarn_app_mapreduce_am_command_opts'),
        'yarn.nodemanager.resource.memory-mb': (
            'NODEMANAGER', 'yarn_nodemanager_resource_memory_mb'),
        'mapreduce.task.io.sort.mb': (
            'YARN_GATEWAY', 'io_sort_mb'),
        'mapreduce.map.java.opts': (
            'YARN_GATEWAY', 'mapreduce_map_java_opts'),
        'mapreduce.reduce.java.opts': (
            'YARN_GATEWAY', 'mapreduce_reduce_java_opts'),
        'yarn.app.mapreduce.am.resource.mb': (
            'YARN_GATEWAY', 'yarn_app_mapreduce_am_resource_mb')
    },
    'cluster_configs': {
        'dfs.replication': ('HDFS', 'dfs_replication')
    }
}


def get_concrete_cluster():
    cluster = ctu.get_fake_cluster()

    # add configs to cluster
    configs = {"SQOOP": {}, "HUE": {}, "general": {}, "KMS": {}, "HIVE": {},
               "SOLR": {}, "FLUME": {}, "HDFS": {"dfs_replication": 1},
               "KS_INDEXER": {}, "SPARK_ON_YARN": {}, "SENTRY": {}, "YARN": {},
               "ZOOKEEPER": {}, "OOZIE": {}, "HBASE": {}, "IMPALA": {}}
    # cluster is immutable, a work around
    dict.__setitem__(cluster, "cluster_config", configs)

    # add fake remotes to instances
    instances = [i for ng in cluster.node_groups for i in ng.instances]
    for i in instances:
        object.__setattr__(i, 'remote', mock.MagicMock())

    # add cluster_id to each node group
    for ng in cluster.node_groups:
        dict.__setitem__(ng, "cluster_id", ng.cluster.id)

    # add extra config
    dict.__setitem__(cluster, "extra", {})
    return cluster


def get_fake_worker_instances():
    ng = get_concrete_cluster().node_groups[2]
    return ng.instances


class TestPluginUtils(b.SaharaTestCase):

    def setUp(self):
        super(TestPluginUtils, self).setUp()
        self.plug_utils = pu.AbstractPluginUtils()

    def tearDown(self):
        super(TestPluginUtils, self).tearDown()

    @mock.patch('sahara.config.CONF.disable_event_log')
    @mock.patch('sahara.plugins.cdh.plugin_utils.'
                'CDHPluginAutoConfigsProvider')
    def test_recommend_configs(self, provider, log_cfg):
        fake_plugin_utils = mock.Mock()
        fake_cluster = mock.Mock()
        self.plug_utils.recommend_configs(
            fake_cluster, fake_plugin_utils, False)
        self.assertEqual([mock.call(CONFIGURATION_SCHEMA,
                                    fake_plugin_utils,
                                    fake_cluster,
                                    False)],
                         provider.call_args_list)

    @mock.patch('sahara.config.CONF.disable_event_log')
    @mock.patch('sahara.plugins.cdh.commands.install_packages')
    def test_install_packages(self, install_packages, log_cfg):
        packages = mock.Mock()
        instances = get_fake_worker_instances()
        self.plug_utils.install_packages(instances, packages)

        calls = [mock.call(i.remote().__enter__(), packages)
                 for i in instances]

        install_packages.assert_has_calls(calls, any_order=False)

    @mock.patch('sahara.config.CONF.disable_event_log')
    @mock.patch('sahara.plugins.cdh.commands.start_agent')
    @mock.patch('sahara.plugins.cdh.commands.configure_agent')
    def test_start_cloudera_agents(self, configure_agent,
                                   start_agent, log_cfg):
        instances = get_fake_worker_instances()

        self.plug_utils.start_cloudera_agents(instances)

        cfg_calls = [mock.call(i.remote().__enter__(), 'manager_inst')
                     for i in instances]
        start_calls = [mock.call(i.remote().__enter__()) for i in instances]

        configure_agent.assert_has_calls(cfg_calls, any_order=False)
        start_agent.assert_has_calls(start_calls, any_order=False)

    @mock.patch('sahara.config.CONF.disable_event_log')
    def test_put_hive_hdfs_xml(self, log_cfg):
        cluster = get_concrete_cluster()
        hive_server = cluster.node_groups[1].instances[0]
        self.plug_utils.put_hive_hdfs_xml(cluster)
        with hive_server.remote() as r:
            calls = [mock.call('sudo su - -c "hadoop fs -mkdir -p'
                               ' /user/hdfs/conf" hdfs'),
                     mock.call('sudo su - -c "hadoop fs -put'
                               ' /etc/hive/conf/hive-site.xml'
                               ' /user/hdfs/conf/hive-site.xml" hdfs')]
            r.execute_command.assert_has_calls(calls, any_order=False)

    @mock.patch('sahara.config.CONF.disable_event_log')
    def test_create_hive_hive_directory(self, log_cfg):
        cluster = get_concrete_cluster()
        namenode = cluster.node_groups[1].instances[0]
        self.plug_utils.create_hive_hive_directory(cluster)
        with namenode.remote() as r:
            calls = [mock.call('sudo su - -c "hadoop fs -mkdir -p'
                               ' /tmp/hive-hive" hdfs'),
                     mock.call('sudo su - -c "hadoop fs -chown hive'
                               ' /tmp/hive-hive" hdfs')]
            r.execute_command.assert_has_calls(calls, any_order=False)
