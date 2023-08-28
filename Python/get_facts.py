#!/usr/bin/env python3

from jnpr.junos import Device
import re
import json
import xmltodict
from lxml import etree

srx_devices = ["192.168.3.101", "192.168.3.102", "192.168.3.103", "192.168.3.104"]
for srx in srx_devices:
    with Device(srx) as dev:
        facts = dev.facts
        hostname = facts["hostname"]
        version = facts["version"]
        uptime = facts["RE0"]["up_time"]
        print(f"\nHostname: {hostname}, Version: {version}, Uptime: {uptime}")
        
        data = dev.rpc.get_interface_information(terse=True)
        result = (etree.tostring(data, encoding="unicode"))
        json_data = json.dumps((xmltodict.parse(result)))
        
        resp = json.loads(json_data)["interface-information"]
        
        physical_int = r"ge-0/0/[0-9]"
        logical_int = r"ge-0/0/[0-9]\."
        
        for line in resp["physical-interface"]:
            name = line["name"]
            status = line["oper-status"]
            if re.search(physical_int, name):
                try:
                    ip_address = line["logical-interface"]["address-family"]["interface-address"]["ifa-local"]["#text"]
                    print(f"Interface: {name}, Status: {status}, IP Address: {ip_address}")
                except:
                    print(f"Interface: {name}, Status: {status}, No Logical Interface")
        
        