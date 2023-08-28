#!/usr/bin/env python3


import sys

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectClosedError

with Device(host="192.168.3.101") as dev:
    with Config(dev, mode="exclusive") as cu:
        
        data = """interfaces {
            ge-0/0/1 {
                unit 0 {
                    family inet {
                        address 172.24.1.2/30;
                    }
                }
            }
        }
        
        """
        cu.load(data, format="text")
        diff = cu.diff()
        if diff is not None:
            if cu.commit_check():
                try:
                    cu.commit(confirm=1)
                    commit_now = input("Commit confirmed will be rolled back in 5 minutes. Type YES to commit now: ").upper()
                    if dev and commit_now == "YES":
                        cu.commit()
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