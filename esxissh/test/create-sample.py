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

    nets = esxissh.EsxiNetwork()
    nets.add("VM Network")
    nets.add("private-network-1")

    disks = esxissh.EsxiDisk()
    disks.add('hoge.vmdk', 10, 'thin')
    # disks.add('foobar.vmdk', 5, 'eagerzeroedthick')

    media = esxissh.EsxiMedia()
    media.add('iso', 'cheddar-share/disk2/archive/iso/CentOS-7-x86_64-Minimal-1908.iso')

    # vm作成
    r = esxi.create_vm("z-sample", "WDS100T2B0A", "centos7-64", 2, 2048, nets, disks, media)
    print("create zzz-sample: " + str(r))

    print("=== enter to continue ===")
    input()

    # 作ったvmの削除
    r = esxi.delete_vm("z-sample")
    print("delete zzz-sample: " + str(r))

    esxi.finalize()
