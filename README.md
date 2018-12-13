# Introduction
This script helps to generate a configuration, based on a template, on a per-interface basis while restricting it to interfaces in specified VLANs. This was primarily created for use to apply interface-level authentication commands.

Usage is available via `python generate_interface_config.py` below.

Requires `napalm` module.

See [#getting-started](getting started for details).

# Usage
To run the script interactively, use `pyhton generate_interface_config.py`.

Can be run unattended by provide `-v`, `-u`, and `-p`. This will use default input files for `devices` and `template` file.

If wanting to specify non-default locations for those files, use `-d` and `-t`.

Full help available using `-h` and below:
```
usage: generate_interface_config.py [-h] [-v VLANS] [-u USERNAME]
                                    [-p PASSWORD] [-d DEVICES] [-t TEMPLATE]

Generate configuration templates per interface in specified VLANs.

optional arguments:
  -h, --help            show this help message and exit
  -v VLANS, --vlans VLANS
                        vlan membership of target interfaces (list: 5, 6, 7, 20).
                        For non-interactive use. Will be prompted if not specified.
  -u USERNAME, --username USERNAME
                        username to login with (applies to all devices).
                        For non-interactive use. Will be prompted if not specified.
  -p PASSWORD, --password PASSWORD
                        password to login with (applies to all devices).
                        For non-interactive use. Will be prompted if not specified.
  -d DEVICES, --devices DEVICES
                        target device list (file)
                        default: inputs/target_devices
  -t TEMPLATE, --template TEMPLATE
                        template to generate configs (file)
                        default: inputs/template.j2
```

Output configuration files will be placed in the project root directory using the `[device].txt` naming format.

# Getting started
## Clone the repository
Download or clone the repo:
```
git clone https://github.com/rnwolfe/interface-config-for-vlans.git
```

## Install requirements
Install requirements using pip.
```
pip install -r requirements.txt
```

## Specify the template
Specify a template file. The file format should be Jinja2.

By default, the scriptp will try to load `inputs/template.js`.

The available variables are `{{ interface_label }}` and `{{ vlan }}`.

This repository provides an *example* configuration. You can simply modify this file.

## Specify devices to run against
Specify a devices file. It should be one device (FQDN or IP) per line.

By default, the script will try `inputs/target_devices`. You can simply modify this file.

```
10.1.100.1
10.2.100.1
10.3.100.1
```

## Example Output
**generate_interface_config.py**
```
$ python generate_interface_config.py 92
Will apply configurations to interfacs in the following VLANs: ['92']
Loading configuration template...
10.1.100.1: Enter device username: admin
10.1.100.1: Enter device password:
10.1.100.1: Opening device...
10.1.100.1: Getting interface VLANs...
10.1.100.1: Generating config from template for interfaces in target VLANs...
10.1.100.1: Writing config to 10.1.100.1.txt...
10.1.100.1: Done!
```

**10.1.100.1.txt**
```
interface Gi1/0/1
 ! Interface is in VLAN 92
 authentication open
 authentication event server dead action authorize
 authentication event servere alive action reinitialize
 dot1x pae authenticator
 authentication port-control auto
 ! Example config
interface Gi1/0/6
 ! Interface is in VLAN 92
 authentication open
 authentication event server dead action authorize
 authentication event servere alive action reinitialize
 dot1x pae authenticator
 authentication port-control auto
<...>
 ! Example config
interface Gi1/0/8
 ! Interface is in VLAN 92
 authentication open
 authentication event server dead action authorize
 authentication event servere alive action reinitialize
 dot1x pae authenticator
 authentication port-control auto
 ! Example config
<output breviated>
 ```
