#!/usr/bin/env python3

from jnpr.junos import Device 
from jnpr.junos.utils.config import Config


host = "192.168.3.101"
user = "ayens"
passwd = "junos123"

set_command = "set system login user netauto-1 class superuser"

with Device(host=host, user=user, password=passwd) as dev:
    with Config(dev, mode="private") as conf:
        conf.load(set_command, format="set")
        diff = conf.diff()
        if diff is not None:
            print(diff)
            conf.commit_check()
            conf.commit(confirm=5)  
            print("Device has been loaded successfully.")
            commit = input("Configuration will be rolled back after 5 minutes. Would you like to commit changes now? (y/n)").lower()
            if commit == "y":
                conf.commit()
        else:
            print("Configuration is upto date.")