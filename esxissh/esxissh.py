import paramiko
import re

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
        print("host: " + self.__esxiaddr)
        print("user: " + self.__username)
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
        return self.__vmlist[vmname]["vmid"]

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
        result = None

        stdin, stdout, stderr = self.__client.exec_command("vim-cmd vmsvc/power.on " + vmid)
        if stdout.channel.recv_exit_status() == 0:
            result = True
        else:
            result = False

        stdin.close()
        stdout.close()
        stderr.close()

        return result

    def set_poweroff(self, vmname):
        """vmの電源オフ

        Returns:
            bool: 成功:True / 失敗:False (元々電源offの場合含む)
        """
        vmid = self.get_vmid(vmname)
        result = None

        stdin, stdout, stderr = self.__client.exec_command("vim-cmd vmsvc/power.off " + vmid)
        if stdout.channel.recv_exit_status() == 0:
            result = True
        else:
            result = False

        stdin.close()
        stdout.close()
        stderr.close()

        return result

    def set_shutdown(self, vmname):
        """vmのシャットダウン

        Returns:
            bool: 成功:True / 失敗:False (vmware-tools未インストールによる失敗含む)
        """
        vmid = self.get_vmid(vmname)
        result = None

        stdin, stdout, stderr = self.__client.exec_command("vim-cmd vmsvc/power.shutdown " + vmid)
        if stdout.channel.recv_exit_status() == 0:
            result = True
        else:
            result = False

        stdin.close()
        stdout.close()
        stderr.close()

        return result
