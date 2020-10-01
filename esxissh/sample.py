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
    print("cloud-dev poweron state: " + str(r))

    r = esxi.get_powerstate("desktop")
    print("desktop poweron state: " + str(r))

    #### power on ##############################
    # desktop-centos poweron (TRUE)
    r = esxi.set_poweron("desktop-centos")
    print("desktop-centos poweron: " + str(r))

    # cloud-dev poweron (FALSE)
    r = esxi.set_poweron("cloud-dev")
    print("cloud-dev poweron: " + str(r))

    # desktop poweron (TRUE)
    r = esxi.set_poweron("desktop")
    print("desktop set_poweron: " + str(r))

    print("=== enter to continue ===")
    input()

    #### shutdown ##############################
    # desktop-centos shutdown (TRUE)
    r = esxi.set_shutdown("desktop-centos")
    print("desktop-centos set_shutdown: " + str(r))

    # desktop shutdown (FALSE)
    r = esxi.set_shutdown("desktop")
    print("desktop set_shutdown: " + str(r))

    print("=== enter to continue ===")
    input()

    #### poweroff ##############################
    # desktop-centos poweroff (FALSE)
    r = esxi.set_poweroff("desktop-centos")
    print("desktop-centos set_poweroff: " + str(r))

    # desktop poweroff (TRUE)
    r = esxi.set_poweroff("desktop")
    print("desktop set_poweroff: " + str(r))


    esxi.finalize()
