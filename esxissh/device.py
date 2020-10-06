import esxissh

import configparser

if __name__ == '__main__':
    print("test begin")

    ini = configparser.SafeConfigParser()
    ini.read('authenticate.conf')
    esxihost = ini.get('esxi', 'host')
    username = ini.get('esxi', 'username')
    password = ini.get('esxi', 'password')

    nets = esxissh.EsxiNetwork()
    nets.add("VM Network")
    nets.add("private-network-1")
    print(nets.length())

    print(nets.get(0))
    print(nets.get(1))