import paramiko
import re
import os

class EsxiSsh:
    """EsxiSsh

    ESXiへssh接続してVM操作などを行う(予定)

    Attributes:
        __username (str): ssh username 
        __password (str): ssh password
        __esxiaddr (str): ESXi ipaddr
        __vmlist (obj): result of 'vim-cmd vmsvc/getallvms'
        __client (obj): ssh connection of paramiko
    """

    __vmlist = {}

    def __init__(self, esxiaddr, username, password):
        self.__username = username
        self.__password = password
        self.__esxiaddr = esxiaddr

    def __connection(self):
        # print("host: " + self.__esxiaddr)
        # print("user: " + self.__username)
        self.__client = paramiko.SSHClient()
        self.__client.load_system_host_keys()
        self.__client.connect(self.__esxiaddr, username=self.__username, password=self.__password)

    def __get_vm_list(self):
        stdin, stdout, stderr = self.__client.exec_command("vim-cmd vmsvc/getallvms")
        for line in stdout:
            result = re.match(r'(\d+)\s+(.+?)\s+\[(.+)\] (.+\.vmx)\s+(\S+)\s+(\S+)', line)
            if result:
                self.__vmlist[result.group(2)] = {
                    "vmid": result.group(1),
                    "ds": result.group(3),
                    "file": result.group(4),
                    "guest": result.group(5),
                    "version": result.group(6)
                }
        stdin.close()
        stdout.close()
        stderr.close()


    def initialize(self):
        """初期化処理

        インスタンス作成後まずコールする。
        sshの接続を行う。
        """
        self.__connection()
        self.__get_vm_list()

    def finalize(self):
        """終了処理

        処理完了後にコールする。
        sshの接続を破棄する。
        """
        self.__client.close()

    def get_vmid(self, vmname):
        """vmid取得

        Args:
            vmname: VM名

        Returns:
            vmid
        """
        if self.__vmlist.get(vmname):
            vmid = self.__vmlist[vmname]["vmid"]
        else:
            raise Exception(vmname + ": no such virtual machine")

        return vmid

    def get_vmxfile(self, vmname):
        """vmxファイルパス取得

        Args:
            vmname: VM名

        Returns:
            str: vmx filepath
        """
        #vmxfile = '/vmfs/volumes/' + datastore + '/' + vmname + '/' + vmname + '.vmx'
        return '/vmfs/volumes/' + self.__vmlist[vmname]['ds'] + '/' + self.__vmlist[vmname]['file']

    def get_powerstate(self, vmname):
        """vmの電源on状態を取得

        Args:
            vmname: vm名

        Returns:
            bool: 電源on: True / 電源off: False
        """
        vmid = self.get_vmid(vmname)
        result = None
        stat = None

        stdin, stdout, stderr = self.__client.exec_command("vim-cmd vmsvc/power.getstate " + vmid)
        for line in stdout:
            m = re.match(r'^Powered (.+)', line)
            if m:
                if m.group(1) == "on":
                    result = True
                elif m.group(1) == "off":
                    result = False
                else:
                    stat = result.group(1)

        stdin.close()
        stdout.close()
        stderr.close()

        if result == None:
            raise Exception("unknown state: '" + str(stat) + "'")

        return result

    def set_poweron(self, vmname):
        """vmの電源投入

        Returns:
            bool: 成功:True / 失敗:False (元々電源onの場合含む)
        """
        vmid = self.get_vmid(vmname)
        return self.__exec_vimcmd('vmsvc/power.on', vmid)

    def set_poweroff(self, vmname):
        """vmの電源オフ

        Returns:
            bool: 成功:True / 失敗:False (元々電源offの場合含む)
        """
        vmid = self.get_vmid(vmname)
        return self.__exec_vimcmd('vmsvc/power.off', vmid)

    def set_shutdown(self, vmname):
        """vmのシャットダウン

        Returns:
            bool: 成功:True / 失敗:False (vmware-tools未インストールによる失敗含む)
        """
        vmid = self.get_vmid(vmname)
        return self.__exec_vimcmd('vmsvc/power.shutdown', vmid)

    def create_vm(self, vmname, datastore, guestos, vcpus, memory, network=None, disks=None, media=None):
        """vm作成

        Args:
            vmname (str): vm名
            datastore (str): データストア名
            guestos (str): ゲストOS種別
            vcpus (int): vCPUs数
            memory (int): memoryサイズ(MB)
        """

        try:
            # vmidを取得できる -> 同名のVMが既にある
            self.get_vmid(vmname)
            return None
        except:
            # vmidを取得できるのであれば処理続行
            pass

        vmid = self.__exec_createdummyvm(vmname, datastore)

        result = self.__set_guestos(vmname, datastore, guestos)
        # print("set guest: " + str(result))

        result = self.__set_vcpus(vmname, datastore, vcpus)
        # print("set vcpus: " + str(result))

        result = self.__set_memory(vmname, datastore, memory)
        # print("set memory: " + str(result))

        if (network != None):
            vmxfile = self.get_vmxfile(vmname) #'/vmfs/volumes/' + datastore + '/' + vmname + '/' + vmname + '.vmx'
            self.__set_network(network, vmxfile)

        if (disks != None):
            vmxfile = self.get_vmxfile(vmname)
            self.__set_storage(disks, vmxfile)

        if (media != None):
            vmxfile = self.get_vmxfile(vmname)
            self.__set_mediamount(media, vmxfile)

        self.__reload_vm(vmid)

        return result

    def __reload_vm(self, vmid):
        """vm情報のreload

        vmxファイルを変更した後などにコールすることで変更内容を反映する

        """

        return self.__exec_vimcmd('vmsvc/reload', vmid)

    def __exec_createdummyvm(self, vmname, datastore):
        """vm作成

        vim-cmd vmsvc/createdummyvmを使ったvmテンプレート作成

        Returns:
            int: vmid (失敗時None)
        """
        result = None

        stdin, stdout, stderr = self.__client.exec_command('vim-cmd vmsvc/createdummyvm ' + vmname + ' /vmfs/volumes/' + datastore)
        if stdout.channel.recv_exit_status() == 0:
            result = stdout.readline().rstrip()

        stdin.close()
        stdout.close()
        stderr.close()

        # vmリストを更新
        self.__get_vm_list()

        return result

    def __set_guestos(self, vmname, datastore, guestos):
        vmxfile = self.get_vmxfile(vmname)  #'/vmfs/volumes/' + datastore + '/' + vmname + '/' + vmname + '.vmx'
        return self.__updateline(vmxfile, "guestOS", guestos)

    def __set_vcpus(self, vmname, datastore, vcpus):
        vmxfile = self.get_vmxfile(vmname)  #'/vmfs/volumes/' + datastore + '/' + vmname + '/' + vmname + '.vmx'
        return self.__updateline(vmxfile, "numvcpus", str(vcpus))

    def __set_memory(self, vmname, datastore, memory):
        vmxfile = self.get_vmxfile(vmname)  #'/vmfs/volumes/' + datastore + '/' + vmname + '/' + vmname + '.vmx'
        return self.__updateline(vmxfile, "memSize", str(memory))

    def __updateline(self, file, key, value):
        # 既存行を削除
        stdin, stdout, stderr = self.__client.exec_command("sed -i -e '/^" + key + " /d' " + file)
        result = stdout.channel.recv_exit_status()

        stdin.close()
        stdout.close()
        stderr.close()

        if result != 0:
            return False

        stdin, stdout, stderr = self.__client.exec_command("echo '" + key + " = \"" + value + "\"' >> " + file)
        result = stdout.channel.recv_exit_status()

        stdin.close()
        stdout.close()
        stderr.close()

        return result == 0

    def __set_network(self, network, vmxfile):
        for i in range(network.length()):
            network_define = "ethernet{}.virtualDev = ".format(str(i)) + '"{}"'.format(network.get(i)['virtualDev']) + "\n"
            network_define += "ethernet{}.networkName = ".format(str(i)) + '"{}"'.format(network.get(i)['networkName']) + "\n"
            network_define += "ethernet{}.addressType = ".format(str(i)) + '"{}"'.format(network.get(i)['addressType']) + "\n"
            network_define += "ethernet{}.uptCompatibility = ".format(str(i)) + '"{}"'.format(str(network.get(i)['uptCompatibility']).upper()) + "\n"
            network_define += "ethernet{}.present = ".format(str(i)) + '"{}"'.format(str(network.get(i)['present']).upper()) + "\n"

            command = "cat  >> " + vmxfile + ' << __EOL__' + "\n" + network_define + "__EOL__\n"
            # print(command)
            stdin, stdout, stderr = self.__client.exec_command(command)
            result = stdout.channel.recv_exit_status()

            stdin.close()
            stdout.close()
            stderr.close()

    def __set_storage(self, disks, vmxfile):
        basepath, ext = os.path.splitext(vmxfile)
        vmdkfile = basepath + '.vmdk'
        basedirpath = os.path.dirname(vmxfile)
        # 既存disk削除
        stdin, stdout, stderr = self.__client.exec_command('vmkfstools --deletevirtualdisk ' + vmdkfile)
        if stdout.channel.recv_exit_status() == 0:
            result = True
        else:
            result = False

        stdin.close()
        stdout.close()
        stderr.close()

        # 既存定義削除
        # 本当は↑で削除したvmdkファイル名に対応したSCSIの番号をちゃんと突き合わせて行削除したい。
        # が、さすがにオーバーキルなのとvm作成直後前提ということでscsi0:0固定で処理
        delete_controller = 'scsi0:0'
        stdin, stdout, stderr = self.__client.exec_command("sed -i -e '/^" + delete_controller + "/d' " + vmxfile)
        if stdout.channel.recv_exit_status() == 0:
            result = True
        else:
            result = False

        stdin.close()
        stdout.close()
        stderr.close()

        # disk作成
        for i in range(disks.length()):
            disk_size = disks.get(i)['size']
            disk_format = disks.get(i)['diskformat']
            disk_filename = basedirpath + '/' + disks.get(i)['name']
            stdin, stdout, stderr = self.__client.exec_command('vmkfstools -c ' + str(disk_size) + 'G -d ' + disk_format + ' ' + disk_filename)
            if stdout.channel.recv_exit_status() == 0:
                result = True
            else:
                result = False

            stdin.close()
            stdout.close()
            stderr.close()

            # 定義追加
            disk_define = "scsi0:{}.deviceType = ".format(str(i)) + '"scsi-hardDisk"' + "\n"
            disk_define += "scsi0:{}.filename = ".format(str(i)) + '"{}"'.format(disks.get(i)['name']) + "\n"
            disk_define += "scsi0:{}.present = ".format(str(i)) + '"TRUE"' + "\n"

            command = "cat  >> " + vmxfile + ' << __EOL__' + "\n" + disk_define + "__EOL__\n"
            # print(command)
            stdin, stdout, stderr = self.__client.exec_command(command)
            result = stdout.channel.recv_exit_status()

            stdin.close()
            stdout.close()
            stderr.close()

        # SCSIアダプタ設定
        self.__updateline(vmxfile, "scsi0.virtualDev", disks.virtual_device)

    def __set_mediamount(self, media, vmxfile):
        for i in range(media.length()):
            media_define = "ide0:{}.deviceType = ".format(str(i)) + '"cdrom-image"' + "\n"
            media_define += "ide0:{}.filename = ".format(str(i)) + '"/vmfs/volumes/{}"'.format(media.get(i)['path']) + "\n"
            media_define += "ide0:{}.present = ".format(str(i)) + '"TRUE"' + "\n"

            command = "cat  >> " + vmxfile + ' << __EOL__' + "\n" + media_define + "__EOL__\n"
            stdin, stdout, stderr = self.__client.exec_command(command)
            result = stdout.channel.recv_exit_status()

            stdin.close()
            stdout.close()
            stderr.close()

    def delete_vm(self, vmname):
        """vm削除

        Returns:
            bool: 成功:True / 失敗:False
        """
        vmid = self.get_vmid(vmname)
        return self.__exec_vimcmd('vmsvc/destroy', vmid)

    def __exec_vimcmd(self, subcommand, args):
        """vim-cmd 汎用実行

        stdoutが不要で戻り値だけ取れればよいコマンド実行用

        Return:
            bool: 成功:True / 失敗:False
        """
        result = None
        stdin, stdout, stderr = self.__client.exec_command("vim-cmd " + subcommand + ' ' + args)
        if stdout.channel.recv_exit_status() == 0:
            result = True
        else:
            result = False

        stdin.close()
        stdout.close()
        stderr.close()

        return result

class EsxiNetwork:
    def __init__(self):
        self.nic_list = []

    def add(self, network_name, virtual_dev='vmxnet3', address_type="generated", upt_compatibility=True, present=True):
        self.nic_list.append(
            {
                'virtualDev': virtual_dev,
                'networkName': network_name,
                'addressType': address_type,
                'uptCompatibility': upt_compatibility,
                'present': present
            }
        )

    def length(self):
        return len(self.nic_list)

    def get(self, index):
        return self.nic_list[index]

class EsxiDisk:
    def __init__(self, device="pvscsi"):
        self.disk_list = []
        self.__virtual_dev = device

    @property
    def virtual_device(self):
        return self.__virtual_dev
    @virtual_device.setter
    def virtual_device(self, device):
        self.__virtual_dev = device

    def add(self, name, size, disk_format='thin'):
        self.disk_list.append(
            {
                'name': name,
                'size': size,
                'diskformat': disk_format
            }
        )

    def length(self):
        return len(self.disk_list)

    def get(self, index):
        return self.disk_list[index]

class EsxiMedia:
    def __init__(self):
        self.media_list = []

    def add(self, type, path):
        self.media_list.append(
            {
                'type': type,
                'path': path
            }
        )

    def length(self):
        return len(self.media_list)

    def get(self, index):
        return self.media_list[index]
