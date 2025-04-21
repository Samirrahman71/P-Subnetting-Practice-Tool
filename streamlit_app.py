import streamlit as st
import ipaddress
from subnet_calculator import SubnetCalculator
from typing import Dict, List, Tuple, Optional
import json
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import io
import base64
from PIL import Image
import time

# Set page configuration
st.set_page_config(
    page_title="IP Subnet Calculator Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper functions for network visualizations
def create_subnet_visualization(network_str, subnets=None):
    """
    Create a visual representation of a network and its subnets
    """
    try:
        # Parse the network
        network = ipaddress.IPv4Network(network_str)
        prefix_len = network.prefixlen
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#F0F2F6')
        ax.set_facecolor('#F0F2F6')
        
        # Calculate network size for visualization
        total_addresses = network.num_addresses
        
        # Draw main network box
        main_rect = patches.Rectangle((0, 0), 1, 1, linewidth=2, edgecolor='#1E88E5', facecolor='#bbdefb', alpha=0.7)
        ax.add_patch(main_rect)
        
        # Add network information
        ax.text(0.5, 0.5, f"{network}\n{total_addresses} addresses", 
                horizontalalignment='center', verticalalignment='center',
                fontsize=12, fontweight='bold')
        
        # If subnets are provided, draw them
        if subnets:
            num_subnets = len(subnets)
            width = 1.0 / num_subnets
            
            for i, subnet in enumerate(subnets):
                subnet_obj = ipaddress.IPv4Network(subnet['network_address'])
                subnet_rect = patches.Rectangle((i * width, 0), width, 1, 
                                               linewidth=1, edgecolor='#FFA000',
                                               facecolor='#FFECB3', alpha=0.8)
                ax.add_patch(subnet_rect)
                
                # Add subnet information
                ax.text(i * width + width/2, 0.5, 
                        f"{subnet['network_address']}\n{subnet['num_hosts']} hosts",
                        horizontalalignment='center', verticalalignment='center',
                        fontsize=10)
        
        # Remove axis ticks and spines
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(f"Network Visualization: {network}", fontsize=14, fontweight='bold')
        
        # Convert plot to image
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img = Image.open(buf)
        plt.close(fig)
        
        return img
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None

def get_binary_representation(ip_addr, netmask=None):
    """
    Get binary representation of an IP address and optionally its netmask
    """
    try:
        # Convert IP address to binary
        if isinstance(ip_addr, str):
            ip_addr = ipaddress.IPv4Address(ip_addr)
        
        # Get binary string, remove '0b' prefix and pad to 32 bits
        binary_str = bin(int(ip_addr))[2:].zfill(32)
        
        # Insert dots for readability
        formatted_binary = '.'.join([binary_str[i:i+8] for i in range(0, 32, 8)])
        
        if netmask:
            if isinstance(netmask, str):
                netmask = ipaddress.IPv4Address(netmask)
            
            netmask_binary = bin(int(netmask))[2:].zfill(32)
            netmask_formatted = '.'.join([netmask_binary[i:i+8] for i in range(0, 32, 8)])
            
            # Create visual representation with network and host portions
            prefix_len = bin(int(netmask)).count('1')
            network_part = formatted_binary[:prefix_len].replace('.', '')
            host_part = formatted_binary[prefix_len:].replace('.', '')
            
            # Reinsert dots
            network_with_dots = '.'.join([network_part[i:i+8] for i in range(0, len(network_part), 8) if i < len(network_part)])
            host_with_dots = '.'.join([host_part[i:i+8] for i in range(0, len(host_part), 8) if i < len(host_part)])
            
            return {
                'ip_binary': formatted_binary,
                'netmask_binary': netmask_formatted,
                'network_part': network_with_dots,
                'host_part': host_with_dots,
                'prefix_len': prefix_len
            }
        
        return {'ip_binary': formatted_binary}
        
    except Exception as e:
        return {'error': str(e)}

def create_binary_visualization(ip_data):
    """
    Create a visual representation of binary IP address and its network/host portions
    """
    if 'error' in ip_data:
        return None
    
    html = f"""
    <div style="font-family: monospace; background-color: #2b2b2b; padding: 15px; border-radius: 5px; color: #ffffff;">
        <div style="margin-bottom: 10px;">IP Address Binary:</div>
        <div style="letter-spacing: 2px;">{ip_data['ip_binary']}</div>
    """
    
    if 'netmask_binary' in ip_data:
        html += f"""
        <div style="margin-bottom: 10px; margin-top: 15px;">Subnet Mask Binary:</div>
        <div style="letter-spacing: 2px;">{ip_data['netmask_binary']}</div>
        
        <div style="margin-bottom: 10px; margin-top: 15px;">Network/Host Portions:</div>
        <div style="letter-spacing: 2px;">
            <span style="color: #4CAF50;">{ip_data['network_part']}</span><span style="color: #FFC107;">{'.' if ip_data['host_part'] else ''}{ip_data['host_part']}</span>
        </div>
        <div style="font-size: 0.8em; margin-top: 5px;">
            <span style="color: #4CAF50;">■</span> Network Portion ({ip_data['prefix_len']} bits) &nbsp;&nbsp;
            <span style="color: #FFC107;">■</span> Host Portion ({32 - ip_data['prefix_len']} bits)
        </div>
    """
    
    html += "</div>"
    return html

# Custom CSS with network-themed styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }
    h1, h2, h3 {
        color: #004D99;
        font-family: 'Roboto', sans-serif;
    }
    h1 {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    h2 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #f0f0f5;
        border-radius: 10px 10px 0 0;
        padding: 0 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        white-space: pre-wrap;
        background-color: #f0f0f5;
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        border-bottom: 4px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #004D99;
        font-weight: 600;
        border-bottom: 4px solid #004D99;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.7);
        color: #004D99;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 0 10px 10px;
        padding: 20px;
        border: 1px solid #e6e6ef;
        border-top: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .info-box {
        background-color: #f0f7ff;
        border-left: 5px solid #004D99;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 0 4px 4px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .result-box {
        background-color: #f8fcff;
        border: 1px solid #a3d2ff;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,77,153,0.08);
    }
    .tech-card {
        background-color: #0D1117;
        color: #e6e6e6;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
    }
    .tech-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(to right, #004D99, #00C5FF);
    }
    .stButton>button {
        background-color: #004D99;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0062CC;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        margin-right: 5px;
    }
    .badge-success {
        background-color: #D6F5D6;
        color: #107C10;
        border: 1px solid #71BA71;
    }
    .badge-info {
        background-color: #E5F2FF;
        color: #0078D4;
        border: 1px solid #A9D4FF;
    }
    .badge-warning {
        background-color: #FFF4CE;
        color: #9D5D00;
        border: 1px solid #FFDC88;
    }
    /* Custom styling for network visualization */
    .network-diagram {
        border: 1px solid #dddddd;
        border-radius: 8px;
        padding: 10px;
        background-color: #fafafa;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
    }
    /* Code-style inputs */
    .code-input {
        font-family: 'Courier New', monospace;
        background-color: #f5f8fa;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    /* IP address segments styling */
    .ip-segment {
        display: inline-block;
        background-color: #e9f5ff;
        border: 1px solid #cce5ff;
        padding: 2px 6px;
        margin: 0 2px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    /* Layout improvements */
    .stSelectbox, .stNumberInput {
        padding-bottom: 10px !important;
    }
    /* Data table styling */
    .dataframe tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .dataframe thead th {
        background-color: #004D99;
        color: white;
        font-weight: 600;
    }
    /* Remove top menu and footer */
    header, footer {
        visibility: hidden;
    }
    /* Floating header caption that looks like a terminal */
    .terminal-header {
        background-color: #1E1E1E;
        color: #00FF00;
        font-family: 'Courier New', monospace;
        padding: 6px 15px;
        border-radius: 8px 8px 0 0;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Preload terminal-style animation text
def terminal_text(text, key=None):
    placeholder = st.empty()
    full_text = ""
    
    # Use a placeholder to render the terminal-style text
    terminal_html = f"""
    <div class="tech-card">
        <span style="color:#A2FF5D;">root@network</span>:<span style="color:#5DA4FF;">/subnet-calculator</span>$ {full_text}<span class="blinking">|</span>
    </div>
    """
    placeholder.markdown(terminal_html, unsafe_allow_html=True)
    
    # Uncomment for production to enable animation
    # for char in text:
    #     full_text += char
    #     terminal_html = f"""
    #     <div class="tech-card">
    #         <span style="color:#A2FF5D;">root@network</span>:<span style="color:#5DA4FF;">/subnet-calculator</span>$ {full_text}<span class="blinking">|</span>
    #     </div>
    #     """
    #     placeholder.markdown(terminal_html, unsafe_allow_html=True)
    #     time.sleep(0.02)
    
    # Final text without cursor
    terminal_html = f"""
    <div class="tech-card">
        <span style="color:#A2FF5D;">root@network</span>:<span style="color:#5DA4FF;">/subnet-calculator</span>$ {text}
    </div>
    """
    placeholder.markdown(terminal_html, unsafe_allow_html=True)
    return placeholder

# Initialize the SubnetCalculator
subnet_calc = SubnetCalculator()

# App header with simulated terminal effect
st.markdown('<div class="terminal-header">NETWORK OPERATIONS CENTER v2.5</div>', unsafe_allow_html=True)

# App title and description with animated terminal effect
st.title("🌐 IP Subnet Calculator Pro")
terminal_text("ifconfig | grep subnet_tool | status")

st.markdown(
    """
    <div class="info-box">
    <h3>Advanced Network Engineering Tool</h3>
    A professional-grade subnet calculator designed for network engineers, CCNA/CCNP professionals, and IT infrastructure teams.
    Features binary visualization, subnet mapping, and technical analytics for enterprise network planning.
    </div>
    """, 
    unsafe_allow_html=True
)

# Status indicators
st.markdown(
    """
    <div style="display: flex; gap: 15px; margin-bottom: 20px;">
        <div><span class="status-badge badge-success">ONLINE</span> Calculator Engine</div>
        <div><span class="status-badge badge-info">v2.5.4</span> IP Protocol Handler</div>
        <div><span class="status-badge badge-info">READY</span> Binary Analyzer</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Create tabs for different functions
tab1, tab2, tab3, tab4 = st.tabs(["Network Info", "Subnet Division", "Host Count", "Supernet"])

# Tab 1: Network Information
with tab1:
    st.header("Network Analysis & Binary Visualization")
    
    # Add a styled input box with code-like appearance
    st.markdown('<div class="terminal-header">ENTER NETWORK PARAMETERS</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Add CSS class for code-style input
        st.markdown("""
        <style>
        .ip-input div[data-baseweb="input"] > div {
            font-family: 'Courier New', monospace;
            background-color: #f5f8fa;
            border: 1px solid #ddd;
        }
        </style>
        """, unsafe_allow_html=True)
        
        network_input = st.text_input(
            "Enter IP Network (CIDR notation):",
            placeholder="Example: 192.168.1.0/24",
            key="network_input_styled"
        )
    
    with col2:
        st.write("")
        st.write("")
        calculate_button = st.button("📊 Analyze Network")
    
    # Example networks with quick select
    if not network_input:
        st.markdown("<p style='margin-top: -10px; font-size: 0.85rem; color: #666;'><b>Quick Select:</b></p>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("RFC1918 - Class A", help="Private network range - Class A"):
                network_input = "10.0.0.0/8"
                st.session_state.network_input_styled = network_input
                st.experimental_rerun()
        with col2:
            if st.button("RFC1918 - Class B", help="Private network range - Class B"):
                network_input = "172.16.0.0/12"
                st.session_state.network_input_styled = network_input
                st.experimental_rerun()
        with col3:
            if st.button("RFC1918 - Class C", help="Private network range - Class C"):
                network_input = "192.168.0.0/16"
                st.session_state.network_input_styled = network_input
                st.experimental_rerun()
        with col4:
            if st.button("AWS VPC Default", help="Default AWS VPC CIDR block"):
                network_input = "10.0.0.0/16"
                st.session_state.network_input_styled = network_input
                st.experimental_rerun()
    
    if calculate_button and network_input:
        try:
            # Add processing effect
            with st.spinner("Performing binary analysis..."): 
                # Simulate processing with a small delay
                time.sleep(0.5)
                
                # Get network information
                result = subnet_calc.get_network_info(network_input)
                
                # Parse components for visuals
                network = ipaddress.IPv4Network(network_input)
                network_addr = str(network.network_address)
                subnet_mask = str(network.netmask)
                
                # Get binary representations
                binary_data = get_binary_representation(network_addr, subnet_mask)
                
                # Create columns for results
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                
                # Terminal-style header for result
                terminal_out = terminal_text(f"show ip subnet {network_input} | detailed")
                
                # Create tabs for different views
                res_tab1, res_tab2, res_tab3 = st.tabs(["📋 Basic Info", "🔢 Binary View", "📊 Network Map"])
                
                with res_tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("<h3 style='color:#004D99; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>Network Parameters</h3>", unsafe_allow_html=True)
                        
                        # Format the IP segments with styling
                        net_addr_parts = result['network_address'].split('.')
                        broadcast_parts = result['broadcast_address'].split('.')
                        subnet_parts = result['subnet_mask'].split('.')
                        
                        net_addr_html = '.'.join([f"<span class='ip-segment'>{p}</span>" for p in net_addr_parts])
                        broadcast_html = '.'.join([f"<span class='ip-segment'>{p}</span>" for p in broadcast_parts])
                        subnet_html = '.'.join([f"<span class='ip-segment'>{p}</span>" for p in subnet_parts])
                        
                        st.markdown(f"<p><b>Network Address:</b> {net_addr_html}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Broadcast Address:</b> {broadcast_html}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Subnet Mask:</b> {subnet_html}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>CIDR Notation:</b> {result['cidr_notation']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Wildcard Mask:</b> {result.get('wildcard_mask', '255.255.255.255')}</p>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<h3 style='color:#004D99; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 8px;'>Capacity Analysis</h3>", unsafe_allow_html=True)
                        
                        # Add a network class badge with appropriate color
                        class_color = "badge-info"
                        if result['network_class'] == 'A':
                            class_color = "badge-success"
                        elif result['network_class'] == 'C':
                            class_color = "badge-warning"
                            
                        st.markdown(f"<p><b>Network Class:</b> <span class='status-badge {class_color}'>{result['network_class']}</span></p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Total Hosts:</b> {result['num_hosts']:,}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Usable Hosts:</b> {int(result['num_hosts']) - 2:,}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>First Usable Host:</b> {result['first_host']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Last Usable Host:</b> {result['last_host']}</p>", unsafe_allow_html=True)
                        
                        # Add utilization percentage visualization
                        if network.prefixlen < 31:
                            usable_percent = 100 * (int(result['num_hosts']) - 2) / (2**(32-network.prefixlen))
                            st.markdown(f"<p><b>Utilization Efficiency:</b> {usable_percent:.2f}%</p>", unsafe_allow_html=True)
                            st.progress(usable_percent/100)
                
                with res_tab2:
                    st.markdown("<h3 style='color:#004D99; margin-bottom: 10px;'>Binary Representation Analysis</h3>", unsafe_allow_html=True)
                    
                    # Create binary visualization
                    binary_html = create_binary_visualization(binary_data)
                    st.markdown(binary_html, unsafe_allow_html=True)
                    
                    # Add more binary details
                    st.markdown("<h4 style='margin-top: 20px; color:#004D99;'>Subnet Mask Analysis</h4>", unsafe_allow_html=True)
                    
                    prefix_len = network.prefixlen
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Calculate leftover bits
                        leftover_bits = 32 - prefix_len
                        st.markdown(f"<p><b>Network Bits:</b> {prefix_len}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Host Bits:</b> {leftover_bits}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Max Subnets:</b> {2**prefix_len:,}</p>", unsafe_allow_html=True)
                                                
                    with col2:
                        st.markdown(f"<p><b>Max Hosts:</b> {2**leftover_bits:,}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Usable Hosts:</b> {max(0, 2**leftover_bits - 2):,}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p><b>Address Space:</b> {network.num_addresses / (2**32) * 100:.6f}% of IPv4</p>", unsafe_allow_html=True)
                    
                    # Add hexadecimal representation
                    st.markdown("<h4 style='margin-top: 20px; color:#004D99;'>Hexadecimal Representation</h4>", unsafe_allow_html=True)
                    
                    # Convert to hex
                    net_addr_int = int(network.network_address)
                    mask_int = int(network.netmask)
                    bcast_int = int(network.broadcast_address)
                    
                    hex_addr = format(net_addr_int, '08X')
                    hex_mask = format(mask_int, '08X')
                    hex_bcast = format(bcast_int, '08X')
                    
                    st.markdown(f"<div class='tech-card' style='margin-top: 10px;'>", unsafe_allow_html=True)
                    st.markdown(f"<p><b>Network (HEX):</b> 0x{hex_addr}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><b>Netmask (HEX):</b> 0x{hex_mask}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p><b>Broadcast (HEX):</b> 0x{hex_bcast}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with res_tab3:
                    st.markdown("<h3 style='color:#004D99; margin-bottom: 10px;'>Network Map</h3>", unsafe_allow_html=True)
                    
                    # Create network visualization
                    network_img = create_subnet_visualization(network_input)
                    if network_img:
                        st.markdown("<div class='network-diagram'>", unsafe_allow_html=True)
                        st.image(network_img, use_column_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Add technical context based on network size
                    if network.prefixlen < 8:
                        st.info("⚠️ This is a very large network block. Consider proper hierarchical design for subnetting.")
                    elif network.prefixlen < 16:
                        st.info("ℹ️ This is a Class A sized block, suitable for large enterprise deployments.")
                    elif network.prefixlen < 24:
                        st.success("✅ This is a medium-sized network block, good for campus or department-level networks.")
                    else:
                        st.success("✅ This is a smaller network block, appropriate for LANs or smaller segments.")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Technical insights section
                st.markdown("<h3>Technical Insights</h3>", unsafe_allow_html=True)
                
                # Generate relevant technical insights based on the network
                insights = []
                if network.prefixlen < 24:
                    insights.append("This network can be further subnetted for better address utilization.")
                if network.prefixlen > 28:
                    insights.append("Limited host capacity - suitable for point-to-point links or small VLANs.")
                if network.is_private:
                    insights.append(f"This is a private network (RFC1918 compliant) - no internet routability without NAT.")
                if network.prefixlen == 24 and str(network.network_address).startswith("192.168"):
                    insights.append("Standard Class C private subnet - commonly used for home/small office networks.")
                
                # Default insight if none apply
                if not insights:
                    insights.append("Network configuration appears standard. Consider VLSM for optimal address utilization.")
                
                # Display insights in a professional format
                for i, insight in enumerate(insights, 1):
                    st.markdown(f"<p>🔹 <b>Insight {i}:</b> {insight}</p>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 30px; border-left: 4px solid #004D99;">    
    <h3 style="margin-top: 0;">Network Engineer's Guide</h3>
    <p><b>Usage Instructions:</b></p>
    <ol>
        <li>Enter an IP network with CIDR notation (e.g., <code>192.168.1.0/24</code>)</li>
        <li>Click "Analyze Network" to process</li>
        <li>Review the detailed analysis across multiple technical dimensions</li>
        <li>Use the "Binary View" tab to see bit-level technical details</li>
        <li>Examine the "Network Map" for visual representation</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

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
