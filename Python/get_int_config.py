#!/usr/bin/env python3

from jnpr.junos import Device
from lxml import etree


srx_devices = {"192.168.3.101", "192.168.3.102", "192.168.3.103", "192.168.3.104"}
for srx in srx_devices:
    with Device(srx) as dev:
        filter = "<configuration><interfaces><interface><name/></interface></interfaces></configuration>"
        filter2 = "<configuration><interfaces><interface></interface></interfaces></configuration>"
        conf = dev.rpc.get_config(filter_xml=filter2)
        print(etree.tostring(conf, encoding="unicode", pretty_print="true"))