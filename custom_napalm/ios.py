import re

from napalm.ios.ios import IOSDriver

class CustomIOSDriver(IOSDriver):
    """Custom NAPALM Cisco IOS Handler to extend NAPALM IOS Driver."""
    def get_interface_vlans(self):
        """
        Get VLAN information for each interface.

        Example output:
        {
            'Gi1/0/1': '92',
            'Gi1/0/10': '10',
            'Gi1/0/11': 'trunk',
            'Gi1/0/12': '10',
            'Gi1/0/13': '92'
        }"""

        command = 'show interface status'
        output = self._send_command(command)

        return_vlans = {}
        for line in output.splitlines():
            split_line = line.split()
            interface_label = split_line[0]

            # Skip the header row.
            if interface_label == 'Port':
                continue

            pattern = r'^[A-Za-z0-9\/]+\s+.*\s{2,}(trunk|[0-9]{1,4})'
            vlan = re.match(pattern, line)

            return_vlans[interface_label] = vlan.group(1)

        return return_vlans