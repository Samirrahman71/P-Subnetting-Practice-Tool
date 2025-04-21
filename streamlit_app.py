import streamlit as st
import ipaddress
from subnet_calculator import SubnetCalculator
from typing import Dict, List, Tuple, Optional
import json
import os
import sys

# Set page configuration
st.set_page_config(
    page_title="IP Subnet Calculator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 5px solid #1E88E5;
        padding: 10px;
        margin-bottom: 20px;
    }
    .result-box {
        background-color: #f0f7ff;
        border: 1px solid #cce5ff;
        border-radius: 5px;
        padding: 15px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the SubnetCalculator
subnet_calc = SubnetCalculator()

# App title and description
st.title("🌐 IP Subnet Calculator")
st.markdown(
    """
    <div class="info-box">
    A comprehensive tool for IP subnet calculations, planning, and learning. 
    Created for network administrators, students, and IT professionals.
    </div>
    """, 
    unsafe_allow_html=True
)

# Create tabs for different functions
tab1, tab2, tab3, tab4 = st.tabs(["Network Info", "Subnet Division", "Host Count", "Supernet"])

# Tab 1: Network Information
with tab1:
    st.header("Calculate Network Information")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        network_input = st.text_input(
            "Enter IP Network (CIDR notation):",
            placeholder="Example: 192.168.1.0/24"
        )
    
    with col2:
        st.write("")
        st.write("")
        calculate_button = st.button("Calculate Network Info")
    
    if calculate_button and network_input:
        try:
            result = subnet_calc.get_network_info(network_input)
            
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("Network Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Network Address:** {result['network_address']}")
                st.markdown(f"**Broadcast Address:** {result['broadcast_address']}")
                st.markdown(f"**Subnet Mask:** {result['subnet_mask']}")
                st.markdown(f"**CIDR Notation:** {result['cidr_notation']}")
            
            with col2:
                st.markdown(f"**Network Class:** {result['network_class']}")
                st.markdown(f"**Number of Hosts:** {result['num_hosts']}")
                st.markdown(f"**First Usable Host:** {result['first_host']}")
                st.markdown(f"**Last Usable Host:** {result['last_host']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("""
    ### How to use:
    1. Enter an IP address with CIDR notation (e.g., 192.168.1.0/24)
    2. Click "Calculate Network Info"
    3. View detailed information about the network
    """)

# Tab 2: Subnet Division
with tab2:
    st.header("Divide Network into Subnets")
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        subnet_network = st.text_input(
            "Enter IP Network to divide:",
            placeholder="Example: 192.168.1.0/24",
            key="subnet_network"
        )
    
    with col2:
        division_method = st.radio(
            "Division method:",
            options=["By Number of Subnets", "By New Prefix Length"],
            horizontal=True
        )
    
    with col3:
        if division_method == "By Number of Subnets":
            subnet_count = st.number_input("Number of subnets:", min_value=2, value=4, step=1)
            division_value = subnet_count
        else:
            new_prefix = st.number_input("New prefix length:", min_value=0, max_value=32, value=26, step=1)
            division_value = new_prefix
    
    subnet_button = st.button("Calculate Subnets")
    
    if subnet_button and subnet_network:
        try:
            if division_method == "By Number of Subnets":
                result = subnet_calc.subnet_network(subnet_network, subnet_count=division_value)
            else:
                result = subnet_calc.subnet_network(subnet_network, new_prefix=division_value)
            
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader(f"Subnet Division Result ({len(result)} subnets)")
            
            # Create a table for the results
            subnet_data = []
            for i, subnet_info in enumerate(result, 1):
                subnet_data.append({
                    "Subnet #": i,
                    "Network Address": subnet_info["network_address"],
                    "Broadcast": subnet_info["broadcast_address"],
                    "First Host": subnet_info["first_host"],
                    "Last Host": subnet_info["last_host"],
                    "# Hosts": subnet_info["num_hosts"]
                })
            
            st.dataframe(subnet_data, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("""
    ### How to use:
    1. Enter the network to divide (e.g., 192.168.1.0/24)
    2. Choose division method: by number of subnets or by new prefix length
    3. Specify either the number of subnets or the new prefix length
    4. Click "Calculate Subnets" to view the resulting subnet division
    """)

# Tab 3: Find Subnet for Host Count
with tab3:
    st.header("Find Subnet for Host Count")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        host_count = st.number_input(
            "Number of hosts needed:",
            min_value=1,
            value=100,
            step=1
        )
    
    with col2:
        base_network = st.text_input(
            "Base network (optional):",
            placeholder="Example: 192.168.0.0/16",
            key="base_network"
        )
    
    with col3:
        st.write("")
        st.write("")
        host_button = st.button("Find Subnet")
    
    if host_button:
        try:
            if base_network:
                result = subnet_calc.find_subnet_for_hosts(host_count, base_network)
            else:
                result = subnet_calc.find_subnet_for_hosts(host_count)
            
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("Subnet for Host Count")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Required Host Count:** {host_count}")
                st.markdown(f"**CIDR Prefix Length:** /{result['prefix_length']}")
                st.markdown(f"**Subnet Mask:** {result['subnet_mask']}")
            
            with col2:
                st.markdown(f"**Actual Available Hosts:** {result['available_hosts']}")
                if 'network_address' in result:
                    st.markdown(f"**Network Address:** {result['network_address']}")
                    st.markdown(f"**Broadcast Address:** {result['broadcast_address']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("""
    ### How to use:
    1. Enter the number of hosts you need in your subnet
    2. Optionally specify a base network to work within
    3. Click "Find Subnet" to determine the appropriate subnet size
    4. The calculator will show the subnet mask and available host count
    """)

# Tab 4: Supernet Calculation
with tab4:
    st.header("Calculate Supernet")
    
    networks_input = st.text_area(
        "Enter networks (one per line):",
        placeholder="Example:\n192.168.1.0/24\n192.168.2.0/24\n192.168.3.0/24",
        height=150
    )
    
    supernet_button = st.button("Calculate Supernet")
    
    if supernet_button and networks_input:
        try:
            networks_list = [line.strip() for line in networks_input.split("\n") if line.strip()]
            result = subnet_calc.find_supernet(networks_list)
            
            st.markdown("<div class='result-box'>", unsafe_allow_html=True)
            st.subheader("Supernet Result")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Supernet Network:** {result['supernet']}")
                st.markdown(f"**CIDR Notation:** {result['cidr_notation']}")
                st.markdown(f"**Subnet Mask:** {result['subnet_mask']}")
            
            with col2:
                st.markdown(f"**Number of Addresses:** {result['num_addresses']}")
                st.markdown(f"**Networks Included:** {len(networks_list)}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("""
    ### How to use:
    1. Enter multiple networks (one per line)
    2. Click "Calculate Supernet"
    3. View the smallest supernet that contains all the given networks
    4. This is useful for route summarization and efficient routing tables
    """)

# Add footer with app information
st.markdown("""
---
### About this App

This IP Subnet Calculator is built using Python with Streamlit. It provides a comprehensive set
of tools for network engineers, IT professionals, and students learning about IP networking.

**Features:**
- Calculate network information for any CIDR notation
- Divide networks into equal-sized subnets
- Find appropriate subnet size for specific host counts
- Calculate supernets (summarized routes)

[View Source Code on GitHub](https://github.com/Samirrahman71/P-Subnetting-Practice-Tool)
""")
