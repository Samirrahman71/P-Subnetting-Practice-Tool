#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test suite for the IP Subnetting Practice Tool.

This script contains test cases for validating the functionality of the SubnetCalculator class.
It can be run directly to test the subnet calculator functionality.

Author: Samir Rahman
Date: April 2025
"""

import unittest
import ipaddress
from subnet_calculator import SubnetCalculator


class TestSubnetCalculator(unittest.TestCase):
    """
    Test cases for the SubnetCalculator class.
    """

    def test_validate_ip_network(self):
        """Test the validate_ip_network method."""
        # Test CIDR notation
        network = SubnetCalculator.validate_ip_network("192.168.1.0/24")
        self.assertEqual(str(network), "192.168.1.0/24")
        
        # Test IP + netmask format
        network = SubnetCalculator.validate_ip_network("192.168.1.0 255.255.255.0")
        self.assertEqual(str(network), "192.168.1.0/24")
        
        # Test with invalid format
        with self.assertRaises(ValueError):
            SubnetCalculator.validate_ip_network("invalid_network")

    def test_get_network_info(self):
        """Test the get_network_info method."""
        info = SubnetCalculator.get_network_info("192.168.1.0/24")
        
        self.assertEqual(info["Network Address"], "192.168.1.0")
        self.assertEqual(info["Broadcast Address"], "192.168.1.255")
        self.assertEqual(info["Subnet Mask"], "255.255.255.0")
        self.assertEqual(info["Wildcard Mask"], "0.0.0.255")
        self.assertEqual(info["Prefix Length"], "24")
        self.assertEqual(info["Network Class"], "C")
        self.assertEqual(info["Number of Hosts"], "254")
        self.assertEqual(info["IP Range"], "192.168.1.1 - 192.168.1.254")
        self.assertEqual(info["CIDR Notation"], "192.168.1.0/24")

    def test_subnet_network_by_count(self):
        """Test the subnet_network method with subnet count."""
        # Divide a /24 into 4 subnets
        subnets = SubnetCalculator.subnet_network("192.168.1.0/24", num_subnets=4)
        
        self.assertEqual(len(subnets), 4)
        self.assertEqual(str(subnets[0]), "192.168.1.0/26")
        self.assertEqual(str(subnets[1]), "192.168.1.64/26")
        self.assertEqual(str(subnets[2]), "192.168.1.128/26")
        self.assertEqual(str(subnets[3]), "192.168.1.192/26")
        
        # Test with invalid subnet count (not a power of 2)
        with self.assertRaises(ValueError):
            SubnetCalculator.subnet_network("192.168.1.0/24", num_subnets=3)

    def test_subnet_network_by_prefix(self):
        """Test the subnet_network method with prefix length."""
        # Divide a /24 into /26 subnets
        subnets = SubnetCalculator.subnet_network("192.168.1.0/24", new_prefix_length=26)
        
        self.assertEqual(len(subnets), 4)
        self.assertEqual(str(subnets[0]), "192.168.1.0/26")
        self.assertEqual(str(subnets[1]), "192.168.1.64/26")
        self.assertEqual(str(subnets[2]), "192.168.1.128/26")
        self.assertEqual(str(subnets[3]), "192.168.1.192/26")
        
        # Test with invalid prefix length (smaller than original)
        with self.assertRaises(ValueError):
            SubnetCalculator.subnet_network("192.168.1.0/24", new_prefix_length=23)

    def test_find_subnet_for_hosts(self):
        """Test the find_subnet_for_hosts method."""
        # For 100 hosts
        prefix_length = SubnetCalculator.find_subnet_for_hosts(100)
        self.assertEqual(prefix_length, 25)  # /25 can accommodate 126 hosts
        
        # For 500 hosts
        prefix_length = SubnetCalculator.find_subnet_for_hosts(500)
        self.assertEqual(prefix_length, 23)  # /23 can accommodate 510 hosts
        
        # For 1 host
        prefix_length = SubnetCalculator.find_subnet_for_hosts(1)
        self.assertEqual(prefix_length, 31)  # /31 can accommodate 2 hosts
        
        # Test with invalid host count
        with self.assertRaises(ValueError):
            SubnetCalculator.find_subnet_for_hosts(0)

    def test_get_ip_class(self):
        """Test the _get_ip_class method."""
        # Class A
        ip_class = SubnetCalculator._get_ip_class(ipaddress.IPv4Address("10.0.0.1"))
        self.assertEqual(ip_class, "A")
        
        # Class B
        ip_class = SubnetCalculator._get_ip_class(ipaddress.IPv4Address("172.16.0.1"))
        self.assertEqual(ip_class, "B")
        
        # Class C
        ip_class = SubnetCalculator._get_ip_class(ipaddress.IPv4Address("192.168.0.1"))
        self.assertEqual(ip_class, "C")
        
        # Class D (Multicast)
        ip_class = SubnetCalculator._get_ip_class(ipaddress.IPv4Address("224.0.0.1"))
        self.assertEqual(ip_class, "D (Multicast)")
        
        # Class E (Reserved)
        ip_class = SubnetCalculator._get_ip_class(ipaddress.IPv4Address("240.0.0.1"))
        self.assertEqual(ip_class, "E (Reserved)")

    def test_get_supernet(self):
        """Test the get_supernet method."""
        # Test with 2 networks
        supernet = SubnetCalculator.get_supernet(["192.168.1.0/24", "192.168.2.0/24"])
        self.assertEqual(str(supernet), "192.168.0.0/23")
        
        # Test with 4 networks
        supernet = SubnetCalculator.get_supernet([
            "172.16.16.0/24", 
            "172.16.17.0/24", 
            "172.16.18.0/24", 
            "172.16.19.0/24"
        ])
        self.assertEqual(str(supernet), "172.16.16.0/22")
        
        # Test with invalid input
        with self.assertRaises(ValueError):
            SubnetCalculator.get_supernet([])


class TestRealWorldScenarios(unittest.TestCase):
    """
    Test cases simulating real-world network scenarios.
    """

    def test_enterprise_network_division(self):
        """Test dividing an enterprise network for different departments."""
        # Scenario: Enterprise with a /16 network needs to distribute to 16 departments
        enterprise_network = "10.1.0.0/16"
        
        # Divide the network into 16 subnets (/20)
        subnets = SubnetCalculator.subnet_network(enterprise_network, num_subnets=16)
        
        # Verify we get 16 subnets
        self.assertEqual(len(subnets), 16)
        
        # Verify the first and last subnets
        self.assertEqual(str(subnets[0]), "10.1.0.0/20")
        self.assertEqual(str(subnets[15]), "10.1.240.0/20")
        
        # Verify each subnet has the correct number of hosts
        hosts_per_subnet = 2**(32 - 20) - 2  # 4094 hosts per /20
        for subnet in subnets:
            if subnet.prefixlen < 31:  # For networks other than /31 and /32
                self.assertEqual(subnet.num_addresses - 2, hosts_per_subnet)

    def test_small_office_requirements(self):
        """Test finding subnets for small office requirements."""
        # Scenario: Small office needs networks for 25, 60, and 10 hosts
        networks_needed = [
            {"department": "Administration", "hosts": 25},
            {"department": "Operations", "hosts": 60},
            {"department": "Management", "hosts": 10}
        ]
        
        # Find appropriate subnet for each department
        base_network = "192.168.0.0"
        expected_prefixes = {
            "Administration": 27,  # /27 can accommodate 30 hosts
            "Operations": 25,      # /25 can accommodate 126 hosts
            "Management": 28       # /28 can accommodate 14 hosts
        }
        
        for dept_info in networks_needed:
            prefix = SubnetCalculator.find_subnet_for_hosts(dept_info["hosts"])
            self.assertEqual(prefix, expected_prefixes[dept_info["department"]])

    def test_supernetting_scenario(self):
        """Test supernetting for route summarization."""
        # Scenario: Combining contiguous networks for route summarization
        networks = [
            "10.10.0.0/24",
            "10.10.1.0/24",
            "10.10.2.0/24",
            "10.10.3.0/24",
            "10.10.4.0/24",
            "10.10.5.0/24",
            "10.10.6.0/24",
            "10.10.7.0/24",
        ]
        
        # Calculate the supernet
        supernet = SubnetCalculator.get_supernet(networks)
        
        # The supernet should be 10.10.0.0/21
        self.assertEqual(str(supernet), "10.10.0.0/21")
        
        # Verify that the supernet contains all original networks
        for network_str in networks:
            network = ipaddress.IPv4Network(network_str)
            self.assertTrue(
                ipaddress.IPv4Network(str(supernet)).supernet_of(network), 
                f"{supernet} should be a supernet of {network}"
            )


if __name__ == "__main__":
    unittest.main()
