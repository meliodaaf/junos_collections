#!/usr/bin/env python3


import sys

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectClosedError


data = "set system services telnet"
data2 = "set system services ftp"

with Device(host="192.168.31.201", user="ayens", password="iamgroot123") as dev:
    with Config(dev, mode="exclusive") as cu:
        cu.load(data, format="set")
        cu.load(data2, format="set")
        diff = cu.diff()
        if diff is not None:
            print(diff)
            if cu.commit_check():
                try:
                    cu.commit(confirm=1)
                    commit_now = input("Commit confirmed will be rolled back in 5 minutes. Type YES to commit now: ").upper()
                    if dev and commit_now == "YES":
                        cu.commit(comment="Set config test.")
                    else:
                        print("Quitting...")
                        sys.exit()
                except ConnectClosedError:
                    print("Connection error has been detected. Commit confirmed will be rolled back in 1 minute.")
            else:
                cu.rollback()
        else:
            print("No changes made or configuration already exist. Quitting...")
            sys.exit()