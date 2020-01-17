import sys
import os
import getpass
import argparse

import napalm
from netmiko import ConnectHandler

# For pretty terminal output
class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


# main
def analyze_device(username, password, target_devices_file):
    """Script to generate an interface configuration for any interfaces
    on a device that are a member of a specified list of VLANs. """

    # Open target_devices file
    fh = open(target_devices_file, "r")
    devices = [device.strip() for device in fh.readlines()]

    # Get credentials for devices, if not provided:
    if not username:
        username = input("Enter username for devices: ")
    if not password:
        password = getpass.getpass(prompt="Enter password for devices: ")

    for device in devices:
        # Prints to terminal in bold, easier readability
        pretty_hostname = color.BOLD + device + color.END

        # Get interface VLANs for device
        print(f"{pretty_hostname}: Getting interface VLANs...")
        interface_vlans = get_device_interface_vlans(device, username, password)

        if interface_vlans:
            # Generate configuration to apply
            print(f"{pretty_hostname}: Analyzing switch for anamolies...")

            anamolous = []
            for interface, vlan in interface_vlans.items():
                if is_anamolous(interface, vlan):
                    anamolous.append(device)
                    print(
                        f"{color.RED}{pretty_hostname}: {device} appears to be anamolous!"
                    )

        else:
            print(
                f"{color.RED}{pretty_hostname}: Problem getting VLANs from interfaces on {device}!"
            )


def is_anamolous(interface, vlan):
    return vlan != "trunk" and vlan != "routed" and not interface.startswith("Po")


def get_device_interface_vlans(hostname, username, password):
    try:
        # Setup device for napalm
        driver = napalm.get_network_driver("ios")
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


def push_config_to_device(
    hostname, username, password, configs, save=True, debug=False
):
    # Merging, committing, etc. programmatically via NAPALM requires SCP server
    # enabled and config archiving enabled on device.
    # Given that, we are using netmiko directly.

    # Setup device and connect
    device = {
        "device_type": "cisco_ios",
        "ip": hostname,
        "username": username,
        "password": password,
        "port": 22,  # optional, defaults to 22
        "verbose": False,  # optional, defaults to False
    }
    conn = ConnectHandler(**device)

    # Ensure provided configs are in a list format, as needed by send_config_set()
    if type(configs) is not list:
        configs = configs.split("\n")

    try:
        output = conn.send_config_set(configs)
        if debug:
            print(output)
        if save:
            conn.save_config()
        return output
    except Exception as e:
        print(e)
        return False


def write_to_file(config, filename):
    # config should be a string format
    try:
        f = open(f"{filename}.txt", "w")
        f.write(config)
        return True
    except:
        return False
    finally:
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate configuration templates per interface in specified VLANs.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="username to login with (applies to all devices).\nFor non-interactive use. Will be prompted if not specified.",
    )
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="password to login with (applies to all devices).\nFor non-interactive use. Will be prompted if not specified.",
    )
    parser.add_argument(
        "-d",
        "--devices",
        type=str,
        default="inputs/target_devices",
        help="target device list (file)\ndefault: inputs/target_devices",
    )
    args = parser.parse_args()

    analyze_device(
        username=args.username,
        password=args.password,
        target_devices_file=args.devices,
    )

