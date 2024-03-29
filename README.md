# Underground Laboratory Monitoring Script Repository

## For developers

### Requirements

- python3
- python3-pip
- python3-virtualenv

For RedHat family (CentOS, Fedora...),

```
sudo yum install python3 python3-pip python3-virtualenv
```

For CentOS 8, Fedora 18 or later,

```
sudo dnf install python3 python3-pip python3-virtualenv
```

For Debian fimily (Ubuntu...)

```
sudo apt install python3 python3-pip python3-virtualenv
```

### Clone and create virtual environment

```
git clone https://github.com/yemilab/monitoring.git
cd monitoring
python3 -m venv venv
```

## Ansible

TODO: document link

## Service configurations

```
cd supervisor
python service_generator.py
```

## Run supervisorctl

```
sudo .../venv/bin/supervisorctl -c .../supervisor/supervisor.conf
```