DOCUMENTATION = r'''
---
module: esxissh_guest

short_description: Manages virtual machines in ESXi with enable SSH

description:
- This module can be used to create new virtual machines, remove a virtual machine.

author:
- zaki (@zaki-lknr)

requirements:
- python >= 3.6
- Paramiko >= 2.7
- enable SSH on ESXi

options:
  esxiaddress:
    description:
    - The hostname or IP address of SSH on ESXi server
    type: str
  esxiusername:
    description:
    - The username of SSH on ESXi server
    type: str
  esxipassword:
    description:
    - The password of SSH on ESXi server
    type: str
  name:
    description:
    - name of the virtual machine to work with.
    type: str
  guest_id:
    description:
    - Set the guest ID.
    type: str
  datastore:
    description:
    - Specify datastore or datastore cluster to provision virtual machine.
    type: str
  hardware:
    description:
    - Manage virtual machine's hardware attributes.
    type: dict
    suboptions:
      memory_mb:
        type: int
        description: Amount of memory in MB.
      num_cpus:
        type: int
        description: Number of CPUs.
  networks:
    description: A list of networks configurations.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        description: Name of tye portgroup or distributed virtual portgroup for this interface.
      device_type:
        type: str
        description: Virtual network device.
  disk:
    description: A list of disks to add.
    type: list
    elements: dict
    suboptions:
      type:
        type: str
        description: Type of disk.
      size_gb:
        type: int
        description: Disk storage size in gb.
  cdrom:
    description: A list of CD-ROM configurations for the virtual machine
    type: list
    elements: dict
    suboptions:
      type:
        type: str
        description: The type of CD-ROM.
      iso_path:
        type: str
        description: The datastore path to the ISO file to use
  state:
    description: Set the state of the virtual machine.
    elements: str
'''

EXAMPLES = r'''
  - name: create a new virtual machine
    esxissh_guest:
      esxiaddress: '{{ esxiaddr }}'
      esxiusername: '{{ esxiuser }}'
      esxipassword: '{{ esxipass }}'
      name: mv-virtual-machine
      guest_id: centos7-64
      datastore: datastore1
      hardware:
        memory_mb: 4096
        num_cpus: 2
      networks:
        - name: VM Network
          device_type: vmxnet3
        - name: private-network-1
          device_type: vmxnet3
      disk:
        - size_gb: 60
          type: thin
        - size_gb: 20
          type: eagerzeroedthick
      cdrom:
        - type: iso
          iso_path: nfsserv/path/to/iso/CentOS-7-x86_64-Minimal-1908.iso
        - type: iso
          iso_path: nfsserv/path/to/iso/CentOS-8.2.2004-x86_64-minimal.iso
      state: present

  - name: remove a virtual machine
    esxissh_guest:
      esxiaddress: '{{ esxiaddr }}'
      esxiusername: '{{ esxiuser }}'
      esxipassword: '{{ esxipass }}'
      name: mv-virtual-machine
      guest_id: centos7-64
      datastore: datastore1
      state: absent
'''

from ansible.module_utils.basic import AnsibleModule
HAS_ESXISSH_MODULE = False
try:
    from ansible_collections.zaki_lknr.esxissh.plugins.module_utils import esxissh
    HAS_ESXISSH_MODULE = True
except ImportError as e:
    import_error = e

def run_module():

    # パラメタ定義
    module_args = dict(
        esxiaddress=dict(type='str', required=True),
        esxiusername=dict(type='str', required=True),
        esxipassword=dict(type='str', required=True),

        name=dict(type='str', required=True),
        guest_id=dict(type='str', required=True),
        datastore=dict(type='str', required=True),

        hardware=dict(type='dict', required=False),
        networks=dict(type='list', elements='dict', required=False),
        disk=dict(type='list', elements='dict', required=False),
        cdrom=dict(type='list', elements='dict', required=False),

        state=dict(type='str', required=False, default='present'),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
    )

    esxi = esxissh.EsxiSsh(module.params['esxiaddress'], module.params['esxiusername'], module.params['esxipassword'])
    esxi.initialize()

    vmname = module.params['name']
    datastore = module.params['datastore']
    guestid = module.params['guest_id']
    result['name'] = vmname
    result['datastore'] = datastore
    result['guest_id'] = guestid
    if module.params.get('hardware'):
        cpu = module.params['hardware']['num_cpus']
        ram = module.params['hardware']['memory_mb']
        result['hardware'] = module.params['hardware']

    nets = esxissh.EsxiNetwork()
    if module.params.get('networks'):
        nets.add_items(module.params['networks'])
        result['networks'] = module.params['networks']

    disks = esxissh.EsxiDisk()
    if module.params.get('disk'):
        disks.add_items(vmname, module.params['disk'])
        result['disk'] = module.params['disk']

    media = esxissh.EsxiMedia()
    if module.params.get('cdrom'):
        media.add_items(module.params['cdrom'])
        result['cdrom'] = module.params['cdrom']

    try:
        if module.params['state'] == 'absent':
            # VM削除
            delete_vm = esxi.delete_vm(vmname)
            if delete_vm == None:
                # 元から無い場合
                result['changed'] = False
            else:
                # VM削除完了
                result['changed'] = True

        else:
            # VM作成
            create_vm = esxi.create_vm(vmname, datastore, guestid, cpu, ram, nets, disks, media)
            if create_vm == None:
                # VMが既に存在する
                result['changed'] = False
            else:
                # VM作成完了
                result['changed'] = True

    except Exception as err:
        module.fail_json(msg=str(err), **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    if not HAS_ESXISSH_MODULE:
        raise ImportError(import_error)
    main()
