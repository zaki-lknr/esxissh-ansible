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
    vmid = esxi.get_vmid("cloud-dev")
    print("vmid: " + vmid)

    r = esxi.get_powerstate("cloud-dev")
    print("cloud-dev poweron: " + str(r))

    r = esxi.get_powerstate("desktop")
    print("desktop poweron: " + str(r))

    # desktop-centos poweron (TRUE)
    r = esxi.set_poweron("desktop-centos")
    print("desktop-centos poweron: " + str(r))

    # cloud-dev poweron (FALSE)
    r = esxi.set_poweron("cloud-dev")
    print("cloud-dev poweron: " + str(r))

    esxi.finalize()
