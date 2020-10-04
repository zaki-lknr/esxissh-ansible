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

    r = esxi.create_vm("zzz-sample", "WDS100T2B0A", "centos7-64", 2)
    print("create zzz-sample: " + str(r))

    print("=== enter to continue ===")
    input()

    r = esxi.delete_vm("zzz-sample")
    print("delete zzz-sample: " + str(r))

    esxi.finalize()
