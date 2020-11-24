# ESXi-sshd Ansible Modules

sshを有効にしたESXiに接続してゲストOSを操作する。
ssh接続したESXiホスト上で`vim-cmd`コマンド等でVM操作を行うので、無償ライセンスでも利用可能。

## Requirements

- Ansible 2.9+
- Python 3+
- Paramiko 2.7+
- enable SSH on ESXi

## Samples

at [sample-playbook](sample-playbook) directory

## License

[MIT](https://opensource.org/licenses/MIT)
