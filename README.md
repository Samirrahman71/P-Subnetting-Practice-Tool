# 🌐 IP Subnetting Practice Tool

A comprehensive Python-based tool for learning and practicing IPv4 subnetting calculations. This command-line utility helps you calculate subnet information, divide networks into smaller subnets, and determine appropriate subnet masks for a given number of hosts.

## 📚 Understanding IP Subnetting

IP subnetting is the process of dividing an IP network into sub-networks to improve security, performance, and address allocation efficiency. Understanding subnetting is crucial for network administrators and IT professionals.

### Key Concepts

- **IP Address**: A 32-bit number that identifies a device on a network, typically written in dotted-decimal notation (e.g., 192.168.1.1).
- **Subnet Mask**: A 32-bit number that divides an IP address into network and host portions (e.g., 255.255.255.0 or /24 in CIDR notation).
- **CIDR (Classless Inter-Domain Routing)**: A method for allocating IP addresses and routing IP packets, expressed as a network address followed by a slash and the prefix length (e.g., 192.168.1.0/24).
- **Network Address**: The first address in a subnet, with all host bits set to 0.
- **Broadcast Address**: The last address in a subnet, with all host bits set to 1.
- **Usable Host Range**: All addresses between the network and broadcast addresses.
- **Wildcard Mask**: The inverse of a subnet mask, often used in access control lists.

## 🚀 Features

- Calculate detailed network information (network address, broadcast address, usable hosts, etc.)
- Divide a network into a specified number of equal-sized subnets
- Find the appropriate subnet to accommodate a required number of hosts
- Calculate the supernet that encompasses multiple networks
- Interactive mode for exploration and learning
- Command-line interface for quick calculations and automation

## 📋 Requirements

- Python 3.6 or later
- Standard library modules (no external dependencies)

## 🔧 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Samirrahman71/P-Subnetting-Practice-Tool.git
   cd P-Subnetting-Practice-Tool
   ```

2. Make the script executable (Unix/Linux/macOS):
   ```bash
   chmod +x subnet_calculator.py
   ```

## 💻 Usage

### Interactive Mode

Run the tool in interactive mode to explore different subnetting scenarios:

```bash
python subnet_calculator.py interactive
```

### Command-Line Mode

The tool offers several command-line modes for different subnetting tasks:

#### Calculate Network Information

```bash
python subnet_calculator.py info 192.168.1.0/24
```

Example output:
```
=================================
      Network Information       
=================================
Network Address     : 192.168.1.0
Broadcast Address   : 192.168.1.255
Subnet Mask         : 255.255.255.0
Wildcard Mask       : 0.0.0.255
Prefix Length       : 24
Network Class       : C
Number of Hosts     : 254
IP Range            : 192.168.1.1 - 192.168.1.254
CIDR Notation       : 192.168.1.0/24
=================================
```

#### Divide a Network into Subnets

By number of subnets (must be a power of 2):
```bash
python subnet_calculator.py subnet 192.168.1.0/24 -n 4
```

By prefix length:
```bash
python subnet_calculator.py subnet 192.168.1.0/24 -p 26
```

Example output:
```
====================================================================================================
                                      Subnet Information                                      
====================================================================================================
Subnet               Network Address  Broadcast       Mask            Range                          Hosts     
----------------------------------------------------------------------------------------------------
192.168.1.0/26       192.168.1.0      192.168.1.63    255.255.255.192 192.168.1.1 - 192.168.1.62     62        
192.168.1.64/26      192.168.1.64     192.168.1.127   255.255.255.192 192.168.1.65 - 192.168.1.126   62        
192.168.1.128/26     192.168.1.128    192.168.1.191   255.255.255.192 192.168.1.129 - 192.168.1.190  62        
192.168.1.192/26     192.168.1.192    192.168.1.255   255.255.255.192 192.168.1.193 - 192.168.1.254  62        
====================================================================================================
```

#### Find Subnet for Host Count

```bash
python subnet_calculator.py hosts 100
```

With a base network:
```bash
python subnet_calculator.py hosts 100 -b 192.168.1.0
```

Example output:
```
For 100 hosts, you need a /25 subnet (netmask: 255.255.255.128)
This subnet can accommodate 126 hosts

=================================
      Network Information       
=================================
Network Address     : 192.168.1.0
Broadcast Address   : 192.168.1.127
Subnet Mask         : 255.255.255.128
Wildcard Mask       : 0.0.0.127
Prefix Length       : 25
Network Class       : C
Number of Hosts     : 126
IP Range            : 192.168.1.1 - 192.168.1.126
CIDR Notation       : 192.168.1.0/25
=================================
```

#### Find Supernet

```bash
python subnet_calculator.py supernet 192.168.1.0/24 192.168.2.0/24
```

Example output:
```
Supernet that contains all provided networks: 192.168.0.0/23

=================================
      Network Information       
=================================
Network Address     : 192.168.0.0
Broadcast Address   : 192.168.1.255
Subnet Mask         : 255.255.254.0
Wildcard Mask       : 0.0.1.255
Prefix Length       : 23
Network Class       : C
Number of Hosts     : 510
IP Range            : 192.168.0.1 - 192.168.1.254
CIDR Notation       : 192.168.0.0/23
=================================
```

## 📝 Examples

### Example 1: Subnet a Network for Different Departments

Problem: You have a 192.168.10.0/24 network and need to divide it into 4 equal subnets for different departments.

Solution:
```bash
python subnet_calculator.py subnet 192.168.10.0/24 -n 4
```

Result: Four /26 networks will be created:
- Marketing: 192.168.10.0/26 (62 hosts)
- Sales: 192.168.10.64/26 (62 hosts)
- Engineering: 192.168.10.128/26 (62 hosts)
- Administration: 192.168.10.192/26 (62 hosts)

### Example 2: Find a Subnet for a New Office

Problem: A new office requires at least 30 IP addresses for devices.

Solution:
```bash
python subnet_calculator.py hosts 30 -b 10.0.0.0
```

Result: A /26 subnet (10.0.0.0/26) will be calculated, which can accommodate 62 hosts.

### Example 3: Determine the Supernet for Multiple Networks

Problem: You need to summarize these networks with a single route: 172.16.16.0/24, 172.16.17.0/24, 172.16.18.0/24, and 172.16.19.0/24.

Solution:
```bash
python subnet_calculator.py supernet 172.16.16.0/24 172.16.17.0/24 172.16.18.0/24 172.16.19.0/24
```

Result: The supernet 172.16.16.0/22 encompasses all four networks.

## 💡 Learning Resources

- For beginners learning subnetting, start with the "hosts" command to understand how prefix lengths relate to available hosts
- To practice subnet division, use the "subnet" command with various networks and subnet counts
- To deepen your understanding of supernetting, experiment with finding common supernets for different combinations of networks

## 🧠 AI-Enhanced Assistant

The IP Subnetting Practice Tool now includes an AI-powered assistant that leverages OpenAI's capabilities to provide smart networking guidance. This feature helps you understand networking concepts, plan networks, and solve complex subnetting problems.

### Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure your OpenAI API key is in the `config.json` file (this file is gitignored for security).

### Features

The AI assistant offers several powerful capabilities:

```bash
# Get an explanation of a networking concept
python ai_assistant.py explain "VLSM subnetting"

# Generate a network plan based on requirements
python ai_assistant.py plan "I need to create a network with 3 departments: IT (100 hosts), Sales (50 hosts), and Management (20 hosts)"

# Get help solving a subnetting problem
python ai_assistant.py solve "How do I divide 192.168.1.0/24 into 6 subnets of different sizes?"

# Generate a practice quiz question
python ai_assistant.py quiz --difficulty hard

# Get troubleshooting guidance
python ai_assistant.py troubleshoot "Two hosts on the same subnet can't communicate"

# Use interactive mode
python ai_assistant.py interactive
```

### Interactive Mode

The interactive mode provides a menu-driven interface to access all AI assistant features. This is the recommended way to explore the capabilities:

```bash
python ai_assistant.py interactive
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.