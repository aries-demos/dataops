from resource_management.core.resources.system import Execute
from resource_management.libraries.script import Script

from resource_management.core.resources.system import File
from resource_management.core.source import InlineTemplate
from resource_management.libraries.functions.check_process_status import check_process_status

from be import install_palo


class PaloFe(Script):
    def install(self, env):
        import params
        env.set_params(params)
        self.install_packages(env)
        install_palo()

    def configure(self, env):
        import params
        env.set_params(params)
        File(
            format("{install_dir}/fe/bin/palo-env.sh"),
            content=InlineTemplate(params.palo_env_content),
            mode=0755,
            owner=params.palo_user,
            group=params.palo_group)
        File(
            format("{install_dir}/fe/conf/fe.conf"),
            content=InlineTemplate(params.fe_conf),
            mode=0755,
            owner=params.palo_user,
            group=params.palo_group)

    def stop(self, env):
        import params
        env.set_params(params)
        Execute(params.install_dir + "/fe/bin/stop_fe.sh")

    def start(self, env):
        import params
        env.set_params(params)
        install_palo()
        self.configure(env)
        Execute(params.install_dir + "/fe/bin/start_fe.sh")

    def status(self, env):
        import params
        check_process_status(params.pid_dir + '/fe.pid')


if __name__ == "__main__":
    PaloFe().execute()
