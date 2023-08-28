#!/usr/bin/env python3

from jnpr.junos import Device
import json
import xmltodict
from lxml import etree


with Device(host='192.168.31.201', user="ayens", password="iamgroot123") as dev:
    config = dev.rpc.get_config()
    res = etree.tostring(config, encoding="unicode")
    json_data = json.dumps(xmltodict.parse(res))
    
    resp = json.loads(json_data)["configuration"]
    
    print(resp["system"]["host-name"])
