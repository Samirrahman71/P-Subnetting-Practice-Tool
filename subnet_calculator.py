#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IP Subnetting Practice Tool

This script provides a set of utilities for working with IPv4 addresses and subnets.
It allows users to calculate subnet information, divide networks into smaller subnets,
and determine appropriate subnet masks for a given number of hosts.

Author: Samir Rahman
Date: April 2025
"""

import ipaddress
import argparse
import sys
import re
from typing import List, Tuple, Dict, Union, Optional


class SubnetCalculator:
    """
    A class for performing various IP subnetting calculations.
    
    This class provides methods to:
    - Calculate network information
    - Divide a network into smaller subnets
    - Find a subnet that can accommodate a given number of hosts
    """

    @staticmethod
    def validate_ip_network(network_str: str) -> ipaddress.IPv4Network:
        """
        Validate and convert a string representation of an IP network to an IPv4Network object.
        
        Args:
            network_str: A string in the format "ip_address/prefix_length" or "ip_address netmask"
            
        Returns:
            An IPv4Network object
            
        Raises:
            ValueError: If the input string is not a valid IP network
        """
        # Check if the input is in CIDR notation
        cidr_match = re.match(r'^(\d+\.\d+\.\d+\.\d+)/(\d+)$', network_str)
        
        # Check if the input is in IP + netmask format
        netmask_match = re.match(r'^(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)$', network_str)
        
        try:
            if cidr_match:
                # Process CIDR notation (e.g. 192.168.1.0/24)
                return ipaddress.IPv4Network(network_str, strict=False)
            elif netmask_match:
                # Process IP + netmask format (e.g. 192.168.1.0 255.255.255.0)
                ip = netmask_match.group(1)
                mask = netmask_match.group(2)
                
                # Convert dotted decimal mask to prefix length
                mask_int = 0
                for octet in mask.split('.'):
                    mask_int = (mask_int << 8) | int(octet)
                
                prefix_len = bin(mask_int).count('1')
                return ipaddress.IPv4Network(f"{ip}/{prefix_len}", strict=False)
            else:
                # Try parsing as is, in case it's a valid network format
                return ipaddress.IPv4Network(network_str, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid IP network format: {e}")

    @staticmethod
    def get_network_info(network_str: str) -> Dict[str, str]:
        """
        Calculate and return detailed information about a network.
        
        Args:
            network_str: A string representing an IP network
            
        Returns:
            A dictionary containing network information
        """
        network = SubnetCalculator.validate_ip_network(network_str)
        
        # Calculate wildcard mask (inverse of subnet mask)
        wildcard_mask = ''
        for octet in network.netmask.packed:
            wildcard_mask += str(255 - octet) + '.'
        wildcard_mask = wildcard_mask[:-1]  # Remove trailing dot
        
        # Prepare the result dictionary
        result = {
            'Network Address': str(network.network_address),
            'Broadcast Address': str(network.broadcast_address),
            'Subnet Mask': str(network.netmask),
            'Wildcard Mask': wildcard_mask,
            'Prefix Length': str(network.prefixlen),
            'Network Class': SubnetCalculator._get_ip_class(network.network_address),
            'Number of Hosts': str(network.num_addresses - 2 if network.prefixlen < 31 else network.num_addresses),
            'IP Range': f"{next(network.hosts()) if network.num_addresses > 1 else network.network_address} - " +
                       f"{list(network.hosts())[-1] if network.num_addresses > 1 else network.broadcast_address}",
            'CIDR Notation': str(network)
        }
        
        return result

    @staticmethod
    def subnet_network(network_str: str, num_subnets: int = 0, new_prefix_length: int = 0) -> List[ipaddress.IPv4Network]:
        """
        Divide a network into smaller subnets.
        
        Args:
            network_str: A string representing an IP network
            num_subnets: Number of subnets to create. Must be a power of 2.
            new_prefix_length: The new prefix length for the subnets.
                               Either num_subnets or new_prefix_length must be provided.
            
        Returns:
            A list of IPv4Network objects representing the subnets
            
        Raises:
            ValueError: If neither num_subnets nor new_prefix_length is provided,
                        or if the resulting subnets are invalid
        """
        network = SubnetCalculator.validate_ip_network(network_str)
        
        # Validate input parameters
        if num_subnets <= 0 and new_prefix_length <= 0:
            raise ValueError("Either number of subnets or new prefix length must be provided")
        
        # Calculate new prefix length based on number of subnets if provided
        if num_subnets > 0:
            if not (num_subnets & (num_subnets - 1) == 0):
                # Check if num_subnets is a power of 2
                raise ValueError("Number of subnets must be a power of 2")
            
            bits_needed = 0
            temp = num_subnets
            while temp > 1:
                temp //= 2
                bits_needed += 1
            
            new_prefix = network.prefixlen + bits_needed
            
            if new_prefix > 32:
                raise ValueError(f"Cannot create {num_subnets} subnets. Maximum possible subnets: {2**(32-network.prefixlen)}")
        else:
            # Use the provided new prefix length
            new_prefix = new_prefix_length
            
            if new_prefix <= network.prefixlen:
                raise ValueError("New prefix length must be greater than the original network's prefix length")
            if new_prefix > 32:
                raise ValueError("Prefix length cannot be greater than 32")
        
        # Generate subnets
        try:
            return list(network.subnets(new_prefix=new_prefix))
        except ValueError as e:
            raise ValueError(f"Error creating subnets: {e}")

    @staticmethod
    def find_subnet_for_hosts(num_hosts: int) -> int:
        """
        Determine the appropriate subnet mask prefix length for a given number of hosts.
        
        Args:
            num_hosts: Number of hosts required
            
        Returns:
            The appropriate prefix length
            
        Raises:
            ValueError: If the number of hosts is invalid
        """
        if num_hosts <= 0:
            raise ValueError("Number of hosts must be positive")
        
        # Add 2 to account for network and broadcast addresses
        total_ips_needed = num_hosts + 2
        
        # Calculate required host bits
        host_bits = 0
        while (1 << host_bits) < total_ips_needed:
            host_bits += 1
            
            # Check if we exceeded IPv4 limits
            if host_bits > 32:
                raise ValueError("Required hosts exceed IPv4 capacity")
        
        # Calculate prefix length (32 - host bits)
        prefix_length = 32 - host_bits
        
        if prefix_length < 0:
            raise ValueError(f"Cannot accommodate {num_hosts} hosts in an IPv4 network")
            
        return prefix_length

    @staticmethod
    def _get_ip_class(ip_address: ipaddress.IPv4Address) -> str:
        """
        Determine the class of an IP address.
        
        Args:
            ip_address: An IPv4Address object
            
        Returns:
            A string representing the IP class ('A', 'B', 'C', 'D', or 'E')
        """
        first_octet = int(ip_address.packed[0])
        
        if first_octet < 128:
            return 'A'
        elif first_octet < 192:
            return 'B'
        elif first_octet < 224:
            return 'C'
        elif first_octet < 240:
            return 'D (Multicast)'
        else:
            return 'E (Reserved)'
    
    @staticmethod
    def get_supernet(networks: List[str]) -> Optional[ipaddress.IPv4Network]:
        """
        Find the smallest supernet that contains all provided networks.
        
        Args:
            networks: A list of network strings
            
        Returns:
            An IPv4Network object representing the supernet, or None if no common supernet exists
            
        Raises:
            ValueError: If any of the input networks is invalid
        """
        if not networks:
            raise ValueError("At least one network must be provided")
        
        # Convert all inputs to IPv4Network objects
        network_objects = [SubnetCalculator.validate_ip_network(net) for net in networks]
        
        try:
            # Find the supernet
            supernet = ipaddress.collapse_addresses(network_objects)
            
            # Return the first (and only) supernet
            for net in supernet:
                return net
            
        except ValueError as e:
            raise ValueError(f"Error finding supernet: {e}")
        
        return None


def print_network_info(info: Dict[str, str]) -> None:
    """
    Print network information in a formatted table.
    
    Args:
        info: A dictionary containing network information
    """
    max_key_len = max(len(key) for key in info.keys())
    
    print("\n" + "=" * (max_key_len + 25))
    print(f"{'Network Information':^{max_key_len + 25}}")
    print("=" * (max_key_len + 25))
    
    for key, value in info.items():
        print(f"{key:{max_key_len}} : {value}")
    
    print("=" * (max_key_len + 25) + "\n")


def print_subnet_list(subnets: List[ipaddress.IPv4Network]) -> None:
    """
    Print a list of subnets in a formatted table.
    
    Args:
        subnets: A list of IPv4Network objects
    """
    if not subnets:
        print("No subnets to display.")
        return
    
    print("\n" + "=" * 100)
    print(f"{'Subnet Information':^100}")
    print("=" * 100)
    print(f"{'Subnet':<20} {'Network Address':<15} {'Broadcast':<15} {'Mask':<15} {'Range':<30} {'Hosts':<10}")
    print("-" * 100)
    
    for i, subnet in enumerate(subnets, 1):
        host_range = f"{next(subnet.hosts()) if subnet.num_addresses > 1 else subnet.network_address} - " + \
                    f"{list(subnet.hosts())[-1] if subnet.num_addresses > 1 else subnet.broadcast_address}"
        
        print(f"{str(subnet):<20} "
              f"{str(subnet.network_address):<15} "
              f"{str(subnet.broadcast_address):<15} "
              f"{str(subnet.netmask):<15} "
              f"{host_range:<30} "
              f"{subnet.num_addresses - 2 if subnet.prefixlen < 31 else subnet.num_addresses:<10}")
    
    print("=" * 100 + "\n")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        An argparse.Namespace object containing the arguments
    """
    parser = argparse.ArgumentParser(
        description="IP Subnetting Practice Tool - Calculate subnet information, divide networks, and more.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest='mode', help='Operating mode')
    
    # Network Info Mode
    info_parser = subparsers.add_parser('info', help='Calculate network information')
    info_parser.add_argument('network', help='Network in CIDR notation (e.g. 192.168.1.0/24) or with mask (e.g. 192.168.1.0 255.255.255.0)')
    
    # Subnet Network Mode
    subnet_parser = subparsers.add_parser('subnet', help='Divide a network into smaller subnets')
    subnet_parser.add_argument('network', help='Network in CIDR notation (e.g. 192.168.1.0/24) or with mask (e.g. 192.168.1.0 255.255.255.0)')
    subnet_group = subnet_parser.add_mutually_exclusive_group(required=True)
    subnet_group.add_argument('-n', '--num-subnets', type=int, help='Number of subnets to create (must be a power of 2)')
    subnet_group.add_argument('-p', '--prefix-length', type=int, help='New prefix length for the subnets')
    
    # Find Subnet for Hosts Mode
    hosts_parser = subparsers.add_parser('hosts', help='Find a subnet that can accommodate a given number of hosts')
    hosts_parser.add_argument('num_hosts', type=int, help='Number of hosts required')
    hosts_parser.add_argument('-b', '--base-network', help='Optional base network to apply the calculated mask to')
    
    # Find Supernet Mode
    supernet_parser = subparsers.add_parser('supernet', help='Find the smallest supernet that contains all provided networks')
    supernet_parser.add_argument('networks', nargs='+', help='Two or more networks in CIDR notation')
    
    # Interactive Mode
    subparsers.add_parser('interactive', help='Enter interactive mode')
    
    return parser.parse_args()


def interactive_mode() -> None:
    """
    Run the subnet calculator in interactive mode.
    """
    print("\n============================================")
    print("   IP Subnetting Practice Tool - Interactive Mode   ")
    print("============================================\n")
    
    while True:
        print("Available operations:")
        print("1. Calculate Network Information")
        print("2. Divide Network into Subnets")
        print("3. Find Subnet for Host Count")
        print("4. Find Supernet")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            network_str = input("Enter network (e.g. 192.168.1.0/24 or 192.168.1.0 255.255.255.0): ").strip()
            try:
                info = SubnetCalculator.get_network_info(network_str)
                print_network_info(info)
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == '2':
            network_str = input("Enter network (e.g. 192.168.1.0/24): ").strip()
            subnet_type = input("Divide by (n)umber of subnets or (p)refix length? (n/p): ").strip().lower()
            
            try:
                if subnet_type == 'n':
                    num_subnets = int(input("Enter number of subnets (must be a power of 2): ").strip())
                    subnets = SubnetCalculator.subnet_network(network_str, num_subnets=num_subnets)
                elif subnet_type == 'p':
                    prefix_length = int(input("Enter new prefix length: ").strip())
                    subnets = SubnetCalculator.subnet_network(network_str, new_prefix_length=prefix_length)
                else:
                    print("Invalid choice. Please enter 'n' or 'p'.")
                    continue
                
                print_subnet_list(subnets)
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == '3':
            try:
                num_hosts = int(input("Enter number of hosts required: ").strip())
                prefix_length = SubnetCalculator.find_subnet_for_hosts(num_hosts)
                print(f"\nFor {num_hosts} hosts, you need a /{prefix_length} subnet (netmask: {str(ipaddress.IPv4Network(f'0.0.0.0/{prefix_length}').netmask)})")
                print(f"This subnet can accommodate {2**(32-prefix_length) - 2} hosts\n")
                
                apply_mask = input("Apply this mask to a specific network? (y/n): ").strip().lower()
                if apply_mask == 'y':
                    base_network = input("Enter base network IP (e.g. 192.168.1.0): ").strip()
                    try:
                        network = ipaddress.IPv4Network(f"{base_network}/{prefix_length}", strict=False)
                        info = SubnetCalculator.get_network_info(str(network))
                        print_network_info(info)
                    except ValueError as e:
                        print(f"Error: {e}")
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == '4':
            networks_input = input("Enter two or more networks separated by spaces: ").strip()
            networks = networks_input.split()
            
            try:
                supernet = SubnetCalculator.get_supernet(networks)
                if supernet:
                    print(f"\nSupernet that contains all provided networks: {supernet}\n")
                    info = SubnetCalculator.get_network_info(str(supernet))
                    print_network_info(info)
                else:
                    print("\nNo common supernet found for the provided networks.\n")
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == '5':
            print("\nExiting IP Subnetting Practice Tool. Goodbye!\n")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
        
        print()  # Extra line for readability


def main() -> None:
    """
    Main function to run the subnet calculator.
    """
    args = parse_arguments()
    
    try:
        if args.mode == 'info':
            info = SubnetCalculator.get_network_info(args.network)
            print_network_info(info)
            
        elif args.mode == 'subnet':
            if args.num_subnets:
                subnets = SubnetCalculator.subnet_network(args.network, num_subnets=args.num_subnets)
            else:
                subnets = SubnetCalculator.subnet_network(args.network, new_prefix_length=args.prefix_length)
            print_subnet_list(subnets)
            
        elif args.mode == 'hosts':
            prefix_length = SubnetCalculator.find_subnet_for_hosts(args.num_hosts)
            print(f"\nFor {args.num_hosts} hosts, you need a /{prefix_length} subnet (netmask: {str(ipaddress.IPv4Network(f'0.0.0.0/{prefix_length}').netmask)})")
            print(f"This subnet can accommodate {2**(32-prefix_length) - 2} hosts\n")
            
            if args.base_network:
                network = ipaddress.IPv4Network(f"{args.base_network}/{prefix_length}", strict=False)
                info = SubnetCalculator.get_network_info(str(network))
                print_network_info(info)
                
        elif args.mode == 'supernet':
            supernet = SubnetCalculator.get_supernet(args.networks)
            if supernet:
                print(f"\nSupernet that contains all provided networks: {supernet}\n")
                info = SubnetCalculator.get_network_info(str(supernet))
                print_network_info(info)
            else:
                print("\nNo common supernet found for the provided networks.\n")
                
        elif args.mode == 'interactive' or args.mode is None:
            interactive_mode()
            
    except ValueError as e:
        print(f"Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
