#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
from resource_management.libraries.functions import check_process_status
from resource_management.libraries.script import Script
from resource_management.libraries.functions import format
from resource_management.core.resources.system import Execute
from storm import storm, install_storm
from service import service
from resource_management.libraries.functions.security_commons import build_expectations, \
    cached_kinit_executor, get_params_from_filesystem, validate_security_config_properties, \
    FILE_TYPE_JAAS_CONF
from setup_ranger_storm import setup_ranger_storm


class Nimbus(Script):
    def install(self, env):
        install_storm()
        self.configure(env)

    def configure(self, env):
        import params
        env.set_params(params)
        storm("nimbus")

    def pre_upgrade_restart(self, env):
        import params
        env.set_params(params)

    def start(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        install_storm()
        self.configure(env)
        setup_ranger_storm(upgrade_type=upgrade_type)
        service("nimbus", action="start")

        if "SUPERVISOR" not in params.config['localComponents']:
            service("logviewer", action="start")

    def stop(self, env):
        import params
        env.set_params(params)
        service("nimbus", action="stop")

        if "SUPERVISOR" not in params.config['localComponents']:
            service("logviewer", action="stop")

    def status(self, env):
        import status_params
        env.set_params(status_params)
        check_process_status(status_params.pid_nimbus)

    def get_log_folder(self):
        import params
        return params.log_dir

    def get_user(self):
        import params
        return params.storm_user

    def get_pid_files(self):
        import status_params
        return [status_params.pid_nimbus]


if __name__ == "__main__":
    Nimbus().execute()
