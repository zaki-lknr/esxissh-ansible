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

    # print(nets.get(0))
    # print(nets.get(1))

    for i in range(nets.length()):
        print("index: " + str(i))
        print(nets.get(i))
        network_define = "ethernet{}.virtualDev = ".format(str(i)) + '"{}"'.format(nets.get(i)['virtualDev'])
        print(network_define)

    print("---- disk ----")
    disks = esxissh.EsxiDisk()
    disks.add('sample.vmdk', 20, 'thin')
    disks.add('hoge.vmdk', 5, 'eagerzeroedthick')
    print(disks)

    for i in range(disks.length()):
        print("index: " + str(i))
        print(disks.get(i))
