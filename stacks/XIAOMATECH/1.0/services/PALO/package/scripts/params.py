#!/usr/bin/env python

from resource_management.libraries.script import Script
from resource_management.libraries.functions import default

# server configurations
config = Script.get_config()
stack_root = Script.get_stack_root()

palo_user = config['configurations']['palo-env']['palo_user']
palo_group = user_group = config['configurations']['cluster-env']['user_group']
log_dir = config['configurations']['palo-env']['palo_log_dir']
pid_dir = config['configurations']['palo-env']['palo_pid_dir']

hostname = config['agentLevelParams']['hostname']
java64_home = config['ambariLevelParams']['java_home']

install_dir = stack_root + '/palo'
download_url = config['configurations']['palo-env']['download_url']
filename = download_url.split('/')[-1]
version_dir = filename.replace('.tar.gz', '').replace('.tgz', '')

fe_conf = config['configurations']['palo-env']['fe_conf']
be_conf = config['configurations']['palo-env']['be_conf']
apache_hdfs_broker_conf = config['configurations']['palo-env'][
    'apache_hdfs_broker_conf']
palo_env_content = config['configurations']['palo-env']['palo_env_content']

palofe_hosts = default("/clusterHostInfo/palofe_hosts", [])
palobe_hosts = default("/clusterHostInfo/palobe_hosts", [])
palohdfsrouter_hosts = default("/clusterHostInfo/palohdfsrouter_hosts", [])

if hostname in palobe_hosts:
    palo_home = install_dir + '/be'
elif hostname in palofe_hosts:
    palo_home = install_dir + '/fe'
else:
    palo_home = install_dir + '/apache_hdfs_broker'

with open('/proc/mounts', 'r') as f:
    mounts = [
        line.split()[1] + '/palo' for line in f.readlines()
        if line.split()[0].startswith('/dev')
        and line.split()[1] not in ['/boot', '/var/log', '/']
    ]

data_dir = ';'.join(mounts)
