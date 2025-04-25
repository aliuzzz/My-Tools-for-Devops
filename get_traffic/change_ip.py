import random
import ipaddress
import configparser
import subprocess

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def generate_random_ipv6_addresses(base_ipv6, use_prefix, count):
    network = ipaddress.IPv6Network(f'{base_ipv6}/{use_prefix}', strict=False)
    addresses = set()    

    for _ in range(count):
        while True:
            random_address_int = network.network_address + random.randint(0, network.num_addresses - 2)
            if random_address_int not in (network.network_address, network.broadcast_address):
                random_address = ipaddress.IPv6Address(random_address_int)
                if random_address not in addresses:
                    addresses.add(random_address)
                    break
    return list(addresses)

def clear_existing_ipv6_addresses(interface):
    try:
        # Remove all existing IPv6 addresses
        subprocess.run(['sudo', 'nmcli', 'con', 'mod', interface, 'ipv6.addresses','','ipv6.gateway','','ipv6.dns','','ipv6.method','disabled'], check=True)
        print(f"Cleared existing IPv6 addresses on {interface}.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while clearing existing IPv6 addresses: {e}")
        raise

def add_ipv6_addresses_to_network_interface(interface, addresses, prefix, gateway, dns):
    try:        
        # Add new IPv6 addresses
        for addr in addresses:
            subprocess.run(['sudo', 'nmcli', 'con', 'mod', interface, f'+ipv6.addresses', f'{addr}/{prefix}', 'ipv6.gateway', gateway, 'ipv6.method', 'manual'], check=True)
        subprocess.run(['sudo', 'nmcli', 'con', 'mod', interface, 'ipv6.dns',f'{dns}'], check=True)
        subprocess.run(['sudo', 'nmcli', 'con', 'reload'], check=True)
        subprocess.run(['sudo', 'nmcli', 'con', 'up', interface], check=True)
        
        print(f"Successfully configured {len(addresses)} IPv6 addresses on {interface}.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while configuring the network interface: {e}")
        raise

def main():
    # Read configuration from file
    config = read_config('/root/xg_download/xg_config.conf')
    
    # Extract values from the [network] section
    network_name = config.get('network', 'network_name')
    ipv6 = config.get('network', 'ipv6')
    prefix = int(config.get('network', 'prefix'))
    use_prefix = int(config.get('network', 'use_prefix'))
    ipv6_gateway = config.get('network', 'ipv6_gateway')
    ipv6_dns = config.get('network', 'ipv6_dns')
    counts = int(config.get('network', 'counts'))

    # Generate the random IPv6 addresses
    random_addresses = generate_random_ipv6_addresses(ipv6, use_prefix, counts)
    # Clear existing IPv6 addresses
    clear_existing_ipv6_addresses(network_name)
    
    # Add the generated IPv6 addresses to the network interface
    add_ipv6_addresses_to_network_interface(network_name, random_addresses, prefix, ipv6_gateway, ipv6_dns)

if __name__ == "__main__":
    main()

