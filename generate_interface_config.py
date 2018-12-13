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
def main(vlan_list, target_devices_file='inputs/target_devices', template_file='interface_template.j2'):
    """Script to generate an interface configuration for any interfaces
    on a device that are a member of a specified list of VLANs. """
    print(target_devices_file)
    # Open target_devices file
    fh = open(target_devices_file, 'r')
    devices = [device.strip() for device in fh.readlines()]

    # Parse VLANs to apply to
    vlan_apply_list = [vlan.strip() for vlan in vlan_list.split(',')]
    print(f'{color.BOLD}Will apply configurations to interfacs in the following VLANs{color.END}: {str(vlan_apply_list)}')

    # Load jinja template
    print(f'{color.BOLD}Loading configuration template...{color.END}')
    loader = jinja2.FileSystemLoader('inputs')
    env = jinja2.Environment(loader=loader)
    template_file = 'interface_template.j2'
    template = env.get_template(template_file)

    # Get credentials for devices:
    username = input(f"Enter username for devices: ")
    password = getpass.getpass(prompt=f"Enter password for devices: ")

    for device in devices:
        # Prints to terminal in bold, easier readability
        pretty_hostname = color.BOLD + device + color.END

        # Get interface VLANs for device
        print(f'{pretty_hostname}: Getting interface VLANs...')
        interface_vlans = get_device_interface_vlans(device, username, password)

        # Generate configuration to apply
        print(f'{pretty_hostname}: Generating config from template for interfaces in target VLANs...')

        output = []
        for interface, vlan in interface_vlans.items():
            if vlan != 'trunk' and (vlan in vlan_apply_list):
                output.append(template.render(interface_label=interface, vlan=vlan))

        config = '\n'.join(output)

        # Write config to file
        print(f'{pretty_hostname}: Writing config to {device}.txt...')
        f = open(f"{device}.txt", "w")
        f.write(config)
        f.close()

        print(f'{pretty_hostname}: Done!')

    # Merging, commiting, etc. programmatically requires SCP server
    # enabled and config archiving enabled on device

def get_device_interface_vlans(hostname, username, password):
    # Setup device for napalm
    driver = napalm.get_network_driver('ios')
    device = driver(hostname=hostname, username=username, password=password)

    # Open device
    device.open()

    # Get VLANs
    interface_vlans = device.get_interface_vlans()

    # Close the device
    device.close()

    return interface_vlans

if __name__ == '__main__':
    if len(sys.argv) < 1:
        sys.exit(1)
        print('Please provide a list of VLANs to apply to.')
    else:
        vlan_list = sys.argv[1]
        device_list = None
        template_file = None
        main(vlan_list)
