from ansible.module_utils.basic import AnsibleModule
#import esxissh  # require "pip install esxissh"
try:
    from ansible.module_utils import esxissh
except ImportError:
    pass

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
        message=''
    )

    esxi = esxissh.EsxiSsh(module.params['esxiaddress'], module.params['esxiusername'], module.params['esxipassword'])
    esxi.initialize()

    vmname = module.params['name']
    cpu = module.params['hardware']['num_cpus']
    ram = module.params['hardware']['memory_mb']
    datastore = module.params['datastore']
    guestid = module.params['guest_id']

    network = module.params['networks']
    # お試し
    nets = esxissh.EsxiNetwork()
    nets.add(network_name=network[0]['name'], virtual_dev=network[0]['device_type'])

    disk = module.params['disk']
    # お試し
    disks = esxissh.EsxiDisk()
    # todo: disk名てきとう
    disks.add(name=vmname+'.vmdk', size=disk[0]['size_gb'], disk_format=disk[0]['type'])

    cdrom = module.params['cdrom']
    # お試し
    media = esxissh.EsxiMedia()
    media.add(type=cdrom[0]['type'], path=cdrom[0]['iso_path'])

    try:
        if module.params['state'] == 'absent':
            # VM削除
            esxi.delete_vm(vmname)
            result['changed'] = True
            result['message'] = vmname + ' is deleted'
            # 最初からない場合の処理がない(例外になる)

        else:
            create_vm = esxi.create_vm(vmname, datastore, guestid, cpu, ram, nets, disks, media)
            if create_vm == None:
                # VMが既に存在する
                result['changed'] = False
                result['message'] = vmname + ' is already exsists'
            else:
                # VM作成完了
                result['changed'] = True
                result['message'] = vmname + ' is created (vmid ' + create_vm + ')'

    except Exception as err:
        module.fail_json(msg=str(err), **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()