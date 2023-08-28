#!/usr/bin/env python3

from jnpr.junos import Device
from jnpr.junos.utils.config import Config

with Device(host="192.168.3.128") as dev:
    with Config(dev, mode="exclusive") as cu:
        cu.lock()
        cu.load(url="/var/host/lab/ijaut/example.conf", overwrite=True)
        cu.commit()
        print("Device configuration loaded successfully.")
        cu.unlock()