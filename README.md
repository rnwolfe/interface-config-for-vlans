# Introduction
This script helps to generate a configuration, based on a template, on a per-interface basis while restricting it to interfaces in specified VLANs. This was primarily created for use to apply interface-level authentication commands.

## Getting started
### Clone the repository
Download or clone the repo:
```
git clone https://github.com/rnwolfe/interface-config-for-vlans.git
```

### Install requirements
Install requirements using pip.
```
pip install -r requirements.txt
```

### Specify the template
Specify the template to generate the configuration in `inputs/interface_template.js`. The variables `{{ interface_label }}` and `{{ vlan }}` are available.

This repository provides an *example* configuration.

### Specify devices to run against
Put one device per line in `inputs/target_devices`.

```
10.1.100.1
10.2.100.1
10.3.100.1
```

### Run the script
To run the script, use:
```
python generate_interface_config.py [vlan_list]
```

For example:
```
python generate_interface_config.py 10.10.100.12 50,51,105,110
```

Output configuration files will be placed in the project root directory using the `[device].txt` naming format.

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
