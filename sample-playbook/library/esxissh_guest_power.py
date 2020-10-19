import os
import sys
from ansible.module_utils.basic import *
sys.path.append("/home/zaki/src/py-esxi-ssh/esxissh")  # <- これ
import esxissh

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

    if (not poweron):
        if module.params['state'] == 'poweron':
            if esxi.set_poweron(module.params['vmname']):
                result['changed']=True
    else:
        if module.params['state'] == 'shutdown':
            if esxi.set_shutdown(module.params['vmname']):
                result['changed']=True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
