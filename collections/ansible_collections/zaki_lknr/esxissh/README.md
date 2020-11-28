# Ansible Collection - zaki_lknr.esxissh

This collection is used to operate vittual machine on ESXi with enabled SSH.

## Requirements

- Ansible 2.9+
- Python 3+
- Paramiko 2.7+
- ESXi 6.5, 6.7 (newer version is not tested)
- enable SSH on ESXi

## Samples

```yaml
- hosts: localhost
  gather_facts: no

  tasks:
  - name: create a new virtual machine
    zaki_lknr.esxissh.esxissh_guest:
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
```

## License

[MIT](https://opensource.org/licenses/MIT)
