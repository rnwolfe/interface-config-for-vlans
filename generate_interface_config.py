import sys
import os
import getpass
import jinja2
import argparse

import napalm
from netmiko import ConnectHandler

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
def generate_and_write_config(vlan_list, username, password, target_devices_file, template_file, commit=False):
    """Script to generate an interface configuration for any interfaces
    on a device that are a member of a specified list of VLANs. """

    # Open target_devices file
    fh = open(target_devices_file, 'r')
    devices = [device.strip() for device in fh.readlines()]

    # Get credentials for devices, if not provided:
    if not username:
        username = input("Enter username for devices: ")
    if not password:
        password = getpass.getpass(prompt="Enter password for devices: ")


    # Get target VLANs, if not provided
    if not vlan_list:
        vlan_list = input("Enter VLANs targeted interfaces should be in (comma seperated): ")

    # Parse VLANs to apply to
    vlan_apply_list = [vlan.strip() for vlan in vlan_list.split(',')]
    print(f'{color.BOLD}Will apply configurations to interfaces in the following VLANs{color.END}: {str(vlan_apply_list)}')

    # Load jinja template
    print(f'{color.BOLD}Loading configuration template...{color.END}')
    loader = jinja2.FileSystemLoader('./')
    env = jinja2.Environment(loader=loader)
    template = env.get_template(template_file)

    for device in devices:
        # Prints to terminal in bold, easier readability
        pretty_hostname = color.BOLD + device + color.END

        # Get interface VLANs for device
        print(f'{pretty_hostname}: Getting interface VLANs...')
        interface_vlans = get_device_interface_vlans(device, username, password)

        if interface_vlans:
            # Generate configuration to apply
            print(f'{pretty_hostname}: Generating config from template for interfaces in target VLANs...')

            output = []
            for interface, vlan in interface_vlans.items():
                if(
                vlan != 'trunk' and
                vlan != 'routed' and
                not interface.startswith('Po') and
                vlan in vlan_apply_list
                ):
                    output.append(template.render(interface_label=interface, vlan=vlan))

            config = '\n'.join(output)
            if commit:
                config_lines = config.split('\n')
                print(f'{pretty_hostname}: Pushing config to {device}...')

                if push_config_to_device(device, username, password, config_lines):
                    print(f'{color.GREEN}{pretty_hostname}: Config successfully committed to {device}!')
                else:
                    print(f'{color.RED}{pretty_hostname}: Config failed to push to {device}!')
            else:
                # Write config to file
                print(f'{pretty_hostname}: Writing config to {device}.txt...')
                print(config)

                if write_config_to_file(config, device):
                    print(f'{color.GREEN}{pretty_hostname}: Done!')
                else:
                    print(f'{color.RED}{pretty_hostname}: Problem writing to file {device}.txt!')
        else:
            print(f'{color.RED}{pretty_hostname}: Problem getting VLANs from interfaces on {device}!')

def get_device_interface_vlans(hostname, username, password):
    try:
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
    except:
        return False

def push_config_to_device(hostname, username, password, configs):
    # Merging, committing, etc. programmatically via NAPALM requires SCP server
    # enabled and config archiving enabled on device.
    # Given that, we are using netmiko directly.

    # Setup device and connect
    device = {
        'device_type': 'cisco_ios',
        'ip':   hostname,
        'username': username,
        'password': password,
        'port' : 22,          # optional, defaults to 22
        'verbose': False,       # optional, defaults to False
    }
    conn = ConnectHandler(**device)

    # Ensure provided configs are in a list format, as needed by send_config_set()
    if type(configs) is not list:
        configs = configs.split('\n')

    try:
        output = conn.send_config_set(configs)
        conn.save_config()
        return output
    except Exception as e:
        print(e)
        return False

def write_config_to_file(config, filename):
    # config should be a string format
    try:
        f = open(f"{filename}.txt", "w")
        f.write(config)
        return True
    except:
        return False
    finally:
        f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate configuration templates per interface in specified VLANs.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--vlans', type=str, help='vlan membership of target interfaces (list: 5, 6, 7, 20).\nFor non-interactive use. Will be prompted if not specified.')
    parser.add_argument('-u', '--username', type=str, help='username to login with (applies to all devices).\nFor non-interactive use. Will be prompted if not specified.')
    parser.add_argument('-p', '--password', type=str, help='password to login with (applies to all devices).\nFor non-interactive use. Will be prompted if not specified.')
    parser.add_argument('-d', '--devices', type=str, default='inputs/target_devices', help='target device list (file)\ndefault: inputs/target_devices')
    parser.add_argument('-t', '--template', type=str, default='inputs/template.j2', help='template to generate configs (file)\ndefault: inputs/template.j2')
    parser.add_argument('-s', '--stage', default=True, action="store_true", help='stage configs to file only\ndefault mode')
    parser.add_argument('-c', '--commit', action="store_true", help='auto commit/push the generated configs to the target devices\nwill overwrite stage flag if set\n')
    args = parser.parse_args()

    generate_and_write_config(vlan_list=args.vlans, username=args.username, password=args.password, target_devices_file=args.devices, template_file=args.template, commit=args.commit)


