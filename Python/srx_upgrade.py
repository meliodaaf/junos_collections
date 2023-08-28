from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.sw import SW
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError
from jnpr.junos.exception import RpcError

import paramiko
import os

# Define a context manager for the devices
class DeviceManager:
    def __init__(self, hostname, username, password):
        self.device = Device(host=hostname, user=username, password=password)

    def __enter__(self):
        self.device.open()
        return self.device

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.device.close()

# Function to backup the configurations on both devices in the chassis cluster and download them to local machine
def backup_configs(primary_dev, backup_dev):
    # Backup the configuration on the primary device
    with Config(primary_dev) as primary_conf:
        primary_conf.lock()
        primary_conf.rollback(0)
        primary_conf.backup('/var/tmp/primary-config-before-upgrade.conf')
        primary_conf.unlock()
        primary_dev.scp('get', '/var/tmp/primary-config-before-upgrade.conf', local_path='./primary-config-before-upgrade.conf')

    # Backup the configuration on the backup device
    with Config(backup_dev) as backup_conf:
        backup_conf.lock()
        backup_conf.rollback(0)
        backup_conf.backup('/var/tmp/backup-config-before-upgrade.conf')
        backup_conf.unlock()
        backup_dev.scp('get', '/var/tmp/backup-config-before-upgrade.conf', local_path='./backup-config-before-upgrade.conf')

# Connect to the primary device in the chassis cluster
with DeviceManager('primary-hostname', 'username', 'password') as dev:
    # Retrieve the current version of the operating system running on the primary device
    current_version = dev.facts['version']

    # Backup the configurations on both devices in the chassis cluster
    with DeviceManager('backup-hostname', 'username', 'password') as backup_dev:
        backup_configs(dev, backup_dev)

    # Upload the new operating system image to both devices in the chassis cluster
    dev.upload_package('/local/path/to/new_os_image.tar.gz', remote_path='/var/tmp/')
    dev.rpc.request_chassis_cluster_package_synchronize()

    # Install the new operating system image on both devices in the chassis cluster
    sw = SW(dev)
    sw.install(package='/var/tmp/new_os_image.tar.gz', progress=True, validate=False, no_copy=True, all_re=True)

    # Reboot the backup device first and monitor its progress
    with DeviceManager('backup-hostname', 'username', 'password') as backup_dev:
        sw = SW(backup_dev)
        sw.reboot()

    # Wait for the backup device to come back online and synchronize with the primary device
    dev.rpc.request_chassis_cluster_redundancy_check()

    # Reboot the primary device and monitor its progress
    sw = SW(dev)
    sw.reboot()

    # Verify the new version of the operating system is running on both devices in the chassis cluster
    dev.rpc.get_route_summary_information()
    backup_dev.rpc.get_route_summary_information()

    # Download the configuration files to local machine
    try:
        transport = paramiko.Transport(('primary-hostname', 22))
        transport.connect(username='username', password='password')
        sftp = paramiko.SFTPClient.from_transport
        sftp.get('/var/tmp/primary-config-before-upgrade.conf', './primary-config-before-upgrade.conf')
        sftp.close()
    except Exception as e:
        print('Error downloading primary configuration file: %s' % e)

    try:
        transport = paramiko.Transport(('backup-hostname', 22))
        transport.connect(username='username', password='password')
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get('/var/tmp/backup-config-before-upgrade.conf', './backup-config-before-upgrade.conf')
        sftp.close()
    except Exception as e:
        print('Error downloading backup configuration file: %s' % e)
