# Copyright (c) 2015 Intel Corporation.
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

from sahara.plugins.cdh.v5_3_0 import plugin_utils as pu
from sahara.tests.unit.plugins.cdh import test_plugin_utils
from sahara.tests.unit.plugins.cdh.v5 import test_plugin_utils_5
from sahara.utils import files


class TestPluginUtilsV530(test_plugin_utils_5.TestPluginUtilsV5):

    def setUp(self):
        super(TestPluginUtilsV530, self).setUp()
        self.plug_utils = pu.PluginUtilsV530()
        self.version = "v5_3_0"

    @mock.patch('sahara.config.CONF.disable_event_log')
    @mock.patch('uuid.uuid4')
    @mock.patch('sahara.conductor.API.cluster_update')
    @mock.patch('sahara.conductor.API.cluster_get')
    def test_configure_sentry(self, cluster_get,
                              cluster_update, uuid4, cfg_log):
        cluster = test_plugin_utils.get_concrete_cluster()
        manager = cluster.node_groups[0].instances[0]
        cluster_get.return_value = cluster
        db_password = 'a8f2939f-ff9f-4659-a333-abc012ee9b2d'
        uuid4.return_value = db_password
        create_db_script = files.get_file_text(
            'plugins/cdh/{version}/resources/create_sentry_db.sql'
                                .format(version=self.version))
        create_db_script = create_db_script % db_password

        self.plug_utils.configure_sentry(cluster)

        with manager.remote() as r:
            cmd_exe_sql = ('PGPASSWORD=$(sudo head -1'
                           ' /var/lib/cloudera-scm-server-db/data/'
                           'generated_password.txt) psql'
                           ' -U cloudera-scm -h localhost -p 7432 -d scm -f'
                           ' script_to_exec.sql')
            cmd_clean = 'rm script_to_exec.sql'
            self.assertEqual(create_db_script, r.write_file_to.call_args[0][1])
            r.execute_command.assert_has_calls([mock.call(cmd_exe_sql),
                                                mock.call(cmd_clean)])
