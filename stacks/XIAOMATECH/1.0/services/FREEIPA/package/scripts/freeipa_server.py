import freeipa
import os, sys
import datetime
import subprocess

from resource_management.libraries.script.script import Script
from resource_management.core.logger import Logger
from resource_management.core.resources.system import Execute
from resource_management.core.resources.packaging import Package
from resource_management.core.resources.system import Directory, File
from resource_management.core.source import InlineTemplate, Template


class FreeipaServer(Script):
    admin_login = 'admin'
    admin_password_file = '/root/admin-password'
    packages = [
        'ipa-server', 'bind', 'bind-dyndb-ldap', 'ipa-server-dns',
        'ipa-server-trust-ad'
    ]
    expected_services = ['chronyd', 'ntpd', 'ns-slapd']

    def install(self, env):
        import params
        env.set_params(params)

        # Execute('/etc/init.d/ambari-server stop')
        # Execute('yum -y remove ambari-server')

        p0 = subprocess.Popen(["hostname", "-f"], stdout=subprocess.PIPE)
        _hostname = p0.communicate()[0].strip()
        if p0.returncode:
            raise OSError("Failed to determine hostname!")

        needed_ports = [88, 123, 389, 464, 636, 8080, 8443]

        self.install_packages(env)

        Package(self.packages)

        admin_password = freeipa.generate_random_password()
        Logger.sensitive_strings[admin_password] = "[PROTECTED]"

        install_command = 'ipa-server-install -U  --realm="%s" \
            --ds-password="%s" --admin-password="%s" --hostname="%s"' % (
            params.realm, params.directory_password, admin_password, _hostname)

        # ipa-server install command. Currently --selfsign is mandatory because
        # of some anoying centos6.5 problems. The underling installer uses an
        # outdated method for the dogtag system which fails.
        # however, on centos7, this option does not exist!

        if params.install_with_dns:
            Package("ipa-server-dns")
            install_command += ' --setup-dns --domain="%s"' % params.domain

            # install_command += ' --setup-dns --domain=freeipa.kave.io'

            if params.forwarders:
                for forwarder in params.forwarders:
                    install_command += ' --forwarder="%s"' % forwarder
            else:
                install_command += ' --no-forwarders'

        p0 = subprocess.Popen(["ipactl", "status"], stdout=subprocess.PIPE)
        p0.communicate()
        ipacheck = p0.returncode
        if ipacheck == 4 or ipacheck == 127:
            # This is a time-consuming command, better to log the output
            Execute(install_command, logoutput=True)
            # write password file
            File(
                "/root/admin-password",
                content=Template(
                    "admin-password.j2", admin_password=admin_password),
                mode=0600)
        # Ensure service is started before trying to interact with it!
        Execute('service ipa start')

        with freeipa.FreeIPA(self.admin_login, self.admin_password_file,
                             False) as fi:
            # set the default shell
            fi.set_default_shell(params.default_shell)
            # Set the admin user shell
            fi.set_user_shell(self.admin_login, params.admin_user_shell)
            # make base accounts
            self.create_base_accounts(env, fi)

            # create initial users and groups
            if "Users" in params.initial_users_and_groups:
                for user in params.initial_users_and_groups["Users"]:
                    if type(user) is str or type(user) is not dict:
                        user = {"username": user}
                    username = user["username"]
                    password = None
                    if username in params.initial_user_passwords:
                        password = params.initial_user_passwords[username]
                    firstname = username
                    lastname = 'auto_generated'
                    if 'firstname' in user:
                        firstname = user['firstname']
                    if 'lastname' in user:
                        lastname = user['lastname']
                    fi.create_user_principal(
                        identity=username,
                        firstname=firstname,
                        lastname=lastname,
                        password=password)
                    if "email" in user:
                        fi.set_user_email(username, user["email"])
            if "Groups" in params.initial_users_and_groups:
                groups = params.initial_users_and_groups["Groups"]
                if type(groups) is dict:
                    groups = [{
                        "name": gname,
                        "members": groups[gname]
                    } for gname in groups]
                for group in groups:
                    freeipa.create_group(group["name"])
                    for user in group["members"]:
                        fi.group_add_member(group["name"], user)
            fi.create_sudorule('allsudo', **(params.initial_sudoers))
        # create robot admin
        self.reset_robot_admin_expire_date(env)
        # if FreeIPA server is not started properly, then the clients will not install
        self.start(env)

    def conf_on_start(self, env):
        import params
        env.set_params(params)
        File(
            "/var/kerberos/krb5kdc/kadm5.acl",
            content=InlineTemplate(params.kadm5acl_template),
            mode=0600)
        File(
            "/root/createkeytabs.py",
            content=Template(
                "createkeytabs.py", scriptpath=os.path.dirname(__file__)),
            mode=0700)

    def start(self, env):
        self.conf_on_start(env)
        self.distribute_robot_admin_credentials(env)
        Execute('service ipa start')

    def stop(self, env):
        Execute('service ipa stop')

    def status(self, env):
        # Pretty weird call here. We need to enforce that the keys are
        # distributed to all agents when they are first installed. This proved
        # to be tricky to achieve in Ambari. This call distributes the
        # credentials to new hosts on each status heartbeat. Pretty weird but
        # for now it serves its purpose.
        try:
            self.distribute_robot_admin_credentials(env)
        except (subprocess.CalledProcessError, OSError, TypeError, ImportError,
                ValueError, KeyError) as e:
            print "Failed to distribute robot credentials during status call: known exception type"
            print e, type(e)
            print sys.exc_info()
        except Exception as e:
            print "Failed to distribute robot credentials during status call: unknown exception type"
            print e, type(e)
            print sys.exc_info()

        Execute('service ipa status')

    def create_base_accounts(self, env, fi):
        """
        fi: a FreeIPA object
        """
        import params

        rm = freeipa.RobotAdmin()

        fi.create_user_principal(
            rm.get_login(),
            groups=['admins'],
            password=freeipa.generate_random_password(),
            password_file=rm.get_password_file())

        fi.set_user_shell(rm.get_login(), params.admin_user_shell)
        # Always create the hadoop group
        fi.create_group('hadoop', 'the hadoop user group')

        # Create ldap bind user
        expiry_date = (datetime.datetime.now() + datetime.timedelta(
            weeks=52 * 10)).strftime('%Y%m%d%H%M%SZ')
        File(
            "/tmp/bind_user.ldif",
            content=Template("bind_user.ldif.j2", expiry_date=expiry_date),
            mode=0600)
        _stat, _stdout, _stderr = Execute(
            'ldapsearch -x -D "cn=directory manager" -w %s "uid=%s"' %
            (params.directory_password, params.ldap_bind_user))
        # is this user already added?
        if "dn: uid=" + params.ldap_bind_user not in _stdout:
            Execute(
                'ldapadd -x -D "cn=directory manager" -w %s -f /tmp/bind_user.ldif'
                % params.directory_password)
        for group in params.ldap_bind_services:
            fi.create_group(group, group + ' user group', ['--nonposix'])

    def reset_robot_admin_expire_date(self, env):
        import params
        env.set_params(params)

        rm = freeipa.RobotAdmin()
        expiry_date = (datetime.datetime.now() +
                       datetime.timedelta(weeks=52)).strftime('%Y%m%d%H%M%SZ')
        File(
            "/tmp/expire_date.ldif",
            content=Template(
                "expire_date.ldif.j2",
                login=rm.get_login(),
                expiry_date=expiry_date),
            mode=0600)
        Execute(
            'ldapadd -x -D "cn=directory manager" -w %s -f /tmp/expire_date.ldif'
            % params.directory_password)

    def distribute_robot_admin_credentials(self, env):
        # If this method is called during status, params will not
        # be available, and therefore I will need to read all_hosts
        # from the database instead
        # trying to import params could result in many possible issues here,
        # most commonly ImportError or KeyError
        try:
            import params
            env.set_params(params)
            all_hosts = params.all_hosts
            user = params.install_distribution_user
            print "using params for all_hosts"
        except (TypeError, ImportError, ValueError, KeyError):
            all_hosts = None

        rm = freeipa.RobotAdmin()
        print "distribution to all hosts with host being", all_hosts
        rm.distribute_password(all_hosts=all_hosts, user=user)


if __name__ == "__main__":
    FreeipaServer().execute()
