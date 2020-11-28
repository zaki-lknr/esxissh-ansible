DOCUMENTATION = r'''
---
module: esxissh_guest_power

short_description: Manages power states of VM in ESXi(enable-ssh)

description:
- Power on / off / shutdown (require vmware-tools) a virtual machine.

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
  vmname:
    description:
    - name of the virtual machine to work with.
    type: str
  state:
    description:
    - Set the state of the virtual machine.
    default: poweron
    type: str
'''

EXAMPLES = r'''
- name: Set the state of a VM to poweron
  esxissh_guest_power:
    esxiaddress: '{{ esxi_hostaddr }}'
    esxiusername: '{{ esxi_sshuser }}'
    esxipassword: '{{ esxi_sshpass }}'
    vmname: mv-virtual-machine
    state: poweron

- name: Set the state of a VM to shutdown (require vmware-tools)
  esxissh_guest_power:
    esxiaddress: '{{ esxi_hostaddr }}'
    esxiusername: '{{ esxi_sshuser }}'
    esxipassword: '{{ esxi_sshpass }}'
    vmname: mv-virtual-machine
    state: shutdown

- name: Set the state of a VM to poweroff
  esxissh_guest_power:
    esxiaddress: '{{ esxi_hostaddr }}'
    esxiusername: '{{ esxi_sshuser }}'
    esxipassword: '{{ esxi_sshpass }}'
    vmname: mv-virtual-machine
    state: poweroff
'''

from ansible.module_utils.basic import AnsibleModule
HAS_ESXISSH_MODULE = False
try:
    from ansible.module_utils import esxissh
    HAS_ESXISSH_MODULE = True
except ImportError as e:
    import_error = e

def run_module():

    # パラメタ定義
    module_args = dict(
        esxiaddress=dict(type='str', required=True),
        esxiusername=dict(type='str', required=True),
        esxipassword=dict(type='str', required=True),
        vmname=dict(type='str', required=True),
        state=dict(type='str', required=False, default='poweron'),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        message=''
    )

    esxi = esxissh.EsxiSsh(module.params['esxiaddress'], module.params['esxiusername'], module.params['esxipassword'])
    esxi.initialize()
    poweron = esxi.get_powerstate(module.params['vmname'])

    try:
        if (not poweron):
            if module.params['state'] == 'poweron':
                if esxi.set_poweron(module.params['vmname']):
                    result['changed']=True
        else:
            if module.params['state'] == 'shutdown':
                if esxi.set_shutdown(module.params['vmname']):
                    result['changed']=True
            elif module.params['state'] == 'poweroff':
                if esxi.set_poweroff(module.params['vmname']):
                    result['changed']=True
    except Exception as err:
        module.fail_json(msg=str(err), **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    if not HAS_ESXISSH_MODULE:
        raise ImportError(import_error)
    main()
