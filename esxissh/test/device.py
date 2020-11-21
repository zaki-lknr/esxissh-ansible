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

    print("---- nic ----")
    nets = esxissh.EsxiNetwork()
    nets.add("VM Network")
    nets.add("private-network-1")
    # print(nets.length())

    # print(nets.get(0))
    # print(nets.get(1))

    for i,dev in enumerate(nets):
        print("index: " + str(i))
        print(dev)
        network_define = "ethernet{}.virtualDev = ".format(str(i)) + '"{}"'.format(dev['virtualDev'])
        print(network_define)

    print("---- disk ----")
    disks = esxissh.EsxiDisk()
    disks.add('sample.vmdk', 20, 'thin')
    disks.add('hoge.vmdk', 5, 'eagerzeroedthick')
    print(disks)
    print(disks.virtual_device)

    for i,dev in enumerate(disks):
        print("index: " + str(i))
        print(dev)

    print("---- media(cd/dvd) ----")
    media = esxissh.EsxiMedia()
    media.add('iso', 'cheddar-share/disk2/archive/iso/CentOS-7-x86_64-Minimal-1908.iso')
    print(media)

    for i,dev in enumerate(media):
        print("index: " + str(i))
        print(dev)
