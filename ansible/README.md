# Ansible

## Install Ansible

        pip install ansible

## Create inventory file




## Run Ansible script with SSH password

For Linux,

1. Install `sshpass`

        dnf install sshpass (for RedHat family)
        apt install sshpass (for Debian family)

2. Start playbook

        ansible-playbook -i hosts --limit rpi -k 10-dev.yml

For Windows or macOS,

1. Install `paramiko`

        pip install paramiko

2. Start playbook

        ansible-playbook -i hosts --limit rpi -c paramiko -k 10-dev.yml
