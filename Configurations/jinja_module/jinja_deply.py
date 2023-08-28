#!/usr/bin/env python3

from jnpr.junos import Device
from jnpr.junos.utils.config import Config

import sys
import yaml


host = "192.168.31.201"
user = "ayens"
passwd = "iamgroot123"
    
filename = "192.168.3.101.yml"
with open(filename, "r") as file:
    data = yaml.safe_load(file)
    with Device(host=host, user=user, password=passwd) as dev:
        with Config(dev, mode="exclusive") as conf:
            conf.load(template_path="j2_template.j2",
                      template_vars=data, format="text")
            conf.pdiff()
            if conf.commit_check():
                commit = input("Configuration is valid. Would you like to commit changes? (y/n) ").lower()
                if commit == "y":
                    conf.commit()
                else:
                    print("Quitting...")
                    sys.exit(0)