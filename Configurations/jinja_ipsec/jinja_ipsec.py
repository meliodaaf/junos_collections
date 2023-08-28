#!/usr/bin/env python3

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import RpcError, RpcTimeoutError


import xmltodict
from lxml import etree

import sys
import yaml
import json
import subprocess

host = "192.168.31.201"
user = "ayens"
passwd = "iamgroot123"
    
filename = "ipsec_yml.yml"


class Colors():
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[36m"
    LIGHTCYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"
    
    
def ping_host(host):
    frame = "."
    while True:
        print(f"\033[2K\r[*] Waiting ICMP response from the management interface{frame}", end="", flush=True)
        ping_process = subprocess.run(["ping", "-c", "1","-W", "1", host], capture_output=True, text=True)
        if ping_process.returncode == 0:
            print(f"\n{Colors.GREEN}Host {host} is now reachable!{Colors.END}")
            return
        frame += "."
        frame = "." if len(frame) == 5 else frame


def load_config():
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
        with Device(host=host, user=user, password=passwd) as dev:
            with Config(dev, mode="private") as conf:
                try:
                    conf.load(template_path="ipsec_template.j2",
                            template_vars=data, format="set")
                    print(f"{Colors.GREEN}Configuration difference:{Colors.END}")
                    conf.pdiff()
                except RpcError as err:
                    print(f"{Colors.RED}Error occured while pushing configuration:{Colors.END}\n{err}")
                    sys.exit(1)
                if conf.commit_check():
                    try:
                        print(f"{Colors.GREEN}Commit Check successful. Executing `commit confirmed 1`.{Colors.END}")
                        conf.commit(confirm=1) # If commit check succeeds, it performs commit confirm
                        commit = input(f"{Colors.GREEN}Commit confirmed will be rolled back in 1 minutes. Type YES to commit now:{Colors.END} ").upper()
                        if commit == "YES" and dev: # confirms that the user confirm and that dev is still reachable
                            conf.commit()
                        else:
                            print("Quitting...")
                            sys.exit(0)
                    except RpcTimeoutError:
                        print(f"{Colors.YELLOW}[!] Connection error has been detected. Commit confirmed will be rolled back in less than 1 minute.{Colors.END}")
                        ping_host(host)
                else:
                    conf.rollback(0) # If commit check fails, revert changes.

def get_interfaces_terse():
    with Device(host=host, user=user, password=passwd) as dev:
        data = dev.rpc.get_interface_information(terse=True)
        result = (etree.tostring(data, encoding="unicode"))
        json_data = json.dumps((xmltodict.parse(result)), indent=4)
        #print(json_data)
        my_object = json.loads(json_data)
        interfaces = my_object["interface-information"]["physical-interface"]
        
        for interface in interfaces:
            name = interface["name"]
            try:
                logical_interface = interface["logical-interface"]
            except:
                pass
            
            if "ge-" in name:
                print(logical_interface["name"], logical_interface["oper-status"])
        
        
if __name__ == "__main__":
    # load_config()
    get_interfaces_terse()