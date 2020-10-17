import sys
import os
sys.path.append((os.path.dirname(__file__) or ".") + "/..")
import esxissh

import configparser

if __name__ == '__main__':
    print("test begin")

    ini = configparser.SafeConfigParser()
    ini.read('authenticate.conf')
    esxihost = ini.get('esxi', 'host')
    username = ini.get('esxi', 'username')
    password = ini.get('esxi', 'password')

    esxi = esxissh.EsxiSsh(esxihost, username, password)
    esxi.initialize()

    print(esxi.get_vmxfile("cloud-dev"))
    print(esxi.get_vmxfile("zzz"))

    esxi.finalize()
