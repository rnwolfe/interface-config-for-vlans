import sys
import os
import getpass
import jinja2

import napalm

# For pretty terminal output
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# main
def main(host, vlan_list, template_file='interface_template.j2'):
    """Script to generate an interface configuration for any interfaces
    on a device that are a member of a specified list of VLANs. """

    # Prints to terminal in bold, easier readability
    pretty_hostname = color.BOLD + host + color.END

    # Parse VLANs to apply to
    vlan_apply_list = [vlan.strip() for vlan in vlan_list.split(',')]
    print(f'{color.BOLD}Will apply configurations to interfacs in the following VLANs{color.END}: {str(vlan_apply_list)}')

    # Load jinja template
    print(f'{color.BOLD}Loading configuration template...{color.END}')
    loader = jinja2.FileSystemLoader('inputs')
    env = jinja2.Environment(loader=loader)
    template_file = 'interface_template.j2'
    template = env.get_template(template_file)

    # Get credentials for device:
    username = input(f"{pretty_hostname}: Enter device username: ")
    password = getpass.getpass(prompt=f"{pretty_hostname}: Enter device password: ")

    # Setup device for napalm
    driver = napalm.get_network_driver('ios')
    device = driver(hostname=host, username=username, password=password)

    print(f'{pretty_hostname}: Opening device...')
    device.open()

    # Get VLANs
    print(f'{pretty_hostname}: Getting interface VLANs...')
    interface_vlans = device.get_interface_vlans()

    # Close the device
    device.close()

    # Generate configuration to apply
    print(f'{pretty_hostname}: Generating config from template for interfaces in target VLANs...')

    output = []
    for interface, vlan in interface_vlans.items():
        if vlan != 'trunk' and (vlan in vlan_apply_list):
            output.append(template.render(interface_label=interface, vlan=vlan))

    config = '\n'.join(output)

    # Write config to file
    print(f'{pretty_hostname}: Writing config to {host}.txt...')
    f = open(f"{host}.txt", "w")
    f.write(config)
    f.close()

    print(f'{pretty_hostname}: Done!')

    # Merging, commiting, etc. programmatically requires SCP server
    # enabled and config archiving enabled on device

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
        # print('Using default parameters.')
        # main('10.1.100.1', '92')
    else:
        device_list = sys.argv[1]
        vlan_list = sys.argv[2]
        template_file = None
        main(device_list, vlan_list, template_file)
