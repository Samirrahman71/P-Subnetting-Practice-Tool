import streamlit as st
import ipaddress
from subnet_calculator import SubnetCalculator
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
from PIL import Image
import pandas as pd
import time

# Must be at the very top - first Streamlit command
st.set_page_config(
    page_title="IP Subnet Calculator",
    page_icon="🌐",
    layout="wide",
)

# Helper functions for visualizations
def create_subnet_visualization(network_str, subnets=None):
    """Create a visual representation of a network and its subnets"""
    try:
        # Parse the network
        network = ipaddress.IPv4Network(network_str)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#f8fafd')
        ax.set_facecolor('#f8fafd')
        
        # Draw main network box
        main_rect = patches.Rectangle((0, 0), 1, 1, linewidth=2, 
                                    edgecolor='#2E7EAF', facecolor='#d0e8f7', alpha=0.7)
        ax.add_patch(main_rect)
        
        # Add network information
        total_addresses = network.num_addresses
        ax.text(0.5, 0.5, f"{network}\n{total_addresses:,} addresses", 
                horizontalalignment='center', verticalalignment='center',
                fontsize=12, fontweight='bold')
        
        # If subnets are provided, draw them
        if subnets:
            num_subnets = len(subnets)
            width = 1.0 / num_subnets
            
            for i, subnet in enumerate(subnets):
                subnet_obj = ipaddress.IPv4Network(subnet['network_address'])
                subnet_rect = patches.Rectangle((i * width, 0), width, 1, 
                                            linewidth=1, edgecolor='#0288D1',
                                            facecolor='#E1F5FE', alpha=0.8)
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
        ax.set_title(f"Network: {network}", fontsize=14)
        
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
    """Get binary representation of an IP address and optionally its netmask"""
    try:
        # Convert IP address to binary
        if isinstance(ip_addr, str):
            ip_addr = ipaddress.IPv4Address(ip_addr)
        
        # Get binary string, pad to 32 bits
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
            network_part = binary_str[:prefix_len]
            host_part = binary_str[prefix_len:]
            
            return {
                'ip_binary': formatted_binary,
                'netmask_binary': netmask_formatted,
                'network_part': network_part,
                'host_part': host_part,
                'prefix_len': prefix_len
            }
        
        return {'ip_binary': formatted_binary}
        
    except Exception as e:
        return {'error': str(e)}

def create_binary_visualization(ip_data):
    """Create a visual representation of binary IP address"""
    if 'error' in ip_data:
        return None
    
    html = f"""
    <div style="font-family: monospace; background-color: #f8fafd; padding: 15px; border-radius: 5px; color: #333333; border: 1px solid #d0e3f7;">
        <div style="margin-bottom: 10px; font-weight: 500;">IP Address in Binary:</div>
        <div style="letter-spacing: 2px;">{ip_data['ip_binary']}</div>
    """
    
    if 'netmask_binary' in ip_data:
        html += f"""
        <div style="margin-bottom: 10px; margin-top: 15px; font-weight: 500;">Subnet Mask in Binary:</div>
        <div style="letter-spacing: 2px;">{ip_data['netmask_binary']}</div>
        
        <div style="margin-bottom: 10px; margin-top: 15px; font-weight: 500;">Network Bits vs Host Bits:</div>
        <div style="letter-spacing: 2px; background-color: #ffffff; padding: 8px; border-radius: 3px; border: 1px solid #e0e9f5;">
        """
        
        # Format each bit with appropriate color
        for i, bit in enumerate(ip_data['ip_binary'].replace('.', '')):
            if i < ip_data['prefix_len']:
                html += f"<span style=\"color: #2E7D32;\">{bit}</span>"
            else:
                html += f"<span style=\"color: #FFA000;\">{bit}</span>"
            # Add space every 8 bits for readability
            if (i+1) % 8 == 0 and i < 31:
                html += " "
                
        html += f"""
        </div>
        <div style="font-size: 0.9em; margin-top: 8px;">
            <span style="color: #2E7D32;">■</span> Network Portion ({ip_data['prefix_len']} bits) &nbsp;&nbsp;
            <span style="color: #FFA000;">■</span> Host Portion ({32 - ip_data['prefix_len']} bits)
        </div>
        """
    
    html += "</div>"
    return html

# Initialize the SubnetCalculator
subnet_calc = SubnetCalculator()

# Custom CSS for improved UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    body {
        color: #333333;
        background-color: #fafafa;
    }
    h1, h2, h3 {
        color: #2E7EAF;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    h1 {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        margin-top: 1rem !important;
    }
    h3 {
        font-size: 1.2rem !important;
        font-weight: 500 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f5f7fa;
        border-radius: 8px 8px 0 0;
        padding: 5px 10px 0 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f5f7fa;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 400;
        font-size: 16px;
        transition: all 0.2s ease;
        border-bottom: 3px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #2E7EAF;
        font-weight: 500;
        border-bottom: 3px solid #2E7EAF;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 0 8px 8px;
        padding: 20px;
        border: 1px solid #e6e9f0;
        border-top: none;
    }
    .info-box {
        background-color: #f4f9ff;
        border-left: 4px solid #2E7EAF;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e0e9f5;
        border-radius: 8px;
        padding: 20px;
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #2E7EAF;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 8px 16px;
        font-weight: 500;
    }
    .status-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        margin-right: 5px;
    }
    .badge-success {
        background-color: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #A5D6A7;
    }
    .badge-info {
        background-color: #E1F5FE;
        color: #0288D1;
        border: 1px solid #B3E5FC;
    }
    .ip-segment {
        display: inline-block;
        background-color: #f0f7ff;
        border: 1px solid #d0e3f7;
        padding: 2px 6px;
        margin: 0 2px;
        border-radius: 4px;
        font-family: monospace;
        font-weight: 500;
    }
    .section-header {
        font-size: 1.2rem;
        color: #2E7EAF;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #eaeff5;
    }
    .divider {
        height: 1px;
        background-color: #eaeff5;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# App title and introduction
st.title("🌐 IP Subnet Calculator")

st.markdown("""
<div class="info-box">
<h3>Network Planning Tool</h3>
A tool for IP subnetting and network planning. Perfect for students, IT professionals, and network administrators.
<br><br>
<b>This tool helps you:</b>
<ul>
    <li>Calculate network information from an IP address</li>
    <li>Divide networks into smaller subnets</li>
    <li>Find the right subnet size for your needs</li>
    <li>Visualize networks and understand binary representations</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Create tabs for different functions
tab1, tab2, tab3, tab4 = st.tabs(["Network Info", "Subnet Division", "Host Count", "Subnet Size"])

# Tab 1: Network Information
with tab1:
    st.header("Network Information")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        network_input = st.text_input(
            "IP Network with CIDR notation:",
            value="192.168.1.0/24",
            placeholder="Example: 192.168.1.0/24",
            help="Enter an IP address followed by a slash and the prefix length (e.g., 192.168.1.0/24)"
        )
    
    with col2:
        st.write("")
        st.write("")
        calculate_button = st.button("Calculate", use_container_width=True)
    
    # Common network examples
    st.write("### Common Networks")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Home Network", key="home"):
            network_input = "192.168.1.0/24"
            st.experimental_rerun()
        if st.button("Large Enterprise", key="enterprise"):
            network_input = "10.0.0.0/8"
            st.experimental_rerun()
    with col2:
        if st.button("Office Network", key="office"):
            network_input = "10.0.0.0/16"
            st.experimental_rerun()
        if st.button("Class B Example", key="classb"):
            network_input = "172.16.0.0/16"
            st.experimental_rerun()
    with col3:
        if st.button("Small Business", key="small"):
            network_input = "192.168.0.0/22"
            st.experimental_rerun()
        if st.button("Localhost", key="localhost"):
            network_input = "127.0.0.0/8"
            st.experimental_rerun()
    
    # Calculation and display
    if calculate_button or network_input:
        try:
            with st.spinner("Calculating network information..."):
                # Get network information
                result = subnet_calc.get_network_info(network_input)
                
            if isinstance(result, dict) and 'error' not in result:
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                
                # Handle different key formats - the calculator returns keys with spaces
                # Map the keys to ensure compatibility
                key_mappings = {
                    'network_address': ['network_address', 'Network Address', 'Network'],
                    'broadcast_address': ['broadcast_address', 'Broadcast Address', 'Broadcast'],
                    'first_host': ['first_host', 'First Host', 'First Usable Host'],
                    'last_host': ['last_host', 'Last Host', 'Last Usable Host'],
                    'subnet_mask': ['subnet_mask', 'Subnet Mask', 'Netmask'],
                    'prefix_length': ['prefix_length', 'Prefix Length', 'Prefix'],
                    'num_hosts': ['num_hosts', 'Number of Hosts', 'Hosts']
                }
                
                # Function to get value using various possible keys
                def get_value(result_dict, possible_keys):
                    for key in possible_keys:
                        if key in result_dict:
                            return result_dict[key]
                    return "N/A"
                
                # Display key network information in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='section-header'>Network Details</div>", unsafe_allow_html=True)
                    network_addr = get_value(result, key_mappings['network_address'])
                    st.markdown(f"**Network Address:** {network_addr}")
                    st.markdown(f"**Broadcast Address:** {get_value(result, key_mappings['broadcast_address'])}")
                    st.markdown(f"**First Usable Host:** {get_value(result, key_mappings['first_host'])}")
                    st.markdown(f"**Last Usable Host:** {get_value(result, key_mappings['last_host'])}")
                with col2:
                    st.markdown("<div class='section-header'>Subnet Information</div>", unsafe_allow_html=True)
                    st.markdown(f"**Subnet Mask:** {get_value(result, key_mappings['subnet_mask'])}")
                    st.markdown(f"**Prefix Length:** {get_value(result, key_mappings['prefix_length'])}")
                    st.markdown(f"**Number of Hosts:** {get_value(result, key_mappings['num_hosts'])}")
                    st.markdown(f"**CIDR Notation:** {network_input}")
                
                # Network visualization
                st.markdown("<div class='section-header'>Network Visualization</div>", unsafe_allow_html=True)
                try:
                    network_img = create_subnet_visualization(network_input)
                    if network_img:
                        st.image(network_img, use_column_width=True)
                    else:
                        st.info("Network visualization could not be generated.")
                except Exception as vis_error:
                    st.warning(f"Network visualization error: {str(vis_error)}")
                
                # Binary representation
                st.markdown("<div class='section-header'>Binary Representation</div>", unsafe_allow_html=True)
                try:
                    # Get network address and subnet mask using key mapping
                    network_addr = get_value(result, key_mappings['network_address'])
                    subnet_mask = get_value(result, key_mappings['subnet_mask'])
                    
                    # Handle potential CIDR notation in network address
                    if '/' in network_addr:
                        network_addr = network_addr.split('/')[0]
                    
                    # Get binary representation
                    binary_data = get_binary_representation(network_addr, subnet_mask)
                    
                    # Display IP segments
                    ip_parts = network_addr.split('.')
                    st.markdown(
                        f"<div style='margin-bottom: 10px;'>IP Address: "
                        f"<span class='ip-segment'>{ip_parts[0]}</span>."
                        f"<span class='ip-segment'>{ip_parts[1]}</span>."
                        f"<span class='ip-segment'>{ip_parts[2]}</span>."
                        f"<span class='ip-segment'>{ip_parts[3]}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    # Display binary visualization
                    binary_html = create_binary_visualization(binary_data)
                    if binary_html:
                        st.markdown(binary_html, unsafe_allow_html=True)
                    else:
                        st.info("Binary visualization could not be generated.")
                    
                    # Explanation
                    with st.expander("Understanding Network & Host Portions"):
                        st.markdown("""
                        **Binary Representation Explained:**
                        
                        * **Green bits:** Network portion - fixed for all hosts in this network
                        * **Yellow bits:** Host portion - can vary to create different host addresses
                        
                        The subnet mask determines how many bits are used for the network vs. host portions. 
                        A longer prefix (higher CIDR number) means more bits are used for the network portion,
                        resulting in more subnets but fewer hosts per subnet.
                        """)
                except Exception as bin_error:
                    st.warning(f"Binary representation error: {str(bin_error)}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {result.get('error', 'Invalid input')}")
                st.info("Please enter a valid IP address in CIDR notation (e.g., 192.168.1.0/24)")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your input format and try again.")

# Tab 2: Subnet Division
with tab2:
    st.header("Divide Network into Subnets")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        parent_network = st.text_input(
            "Parent Network:",
            value="192.168.1.0/24",
            key="parent_network",
            help="The network to divide into subnets"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        division_method = st.radio(
            "Division Method:",
            ["By Number of Subnets", "By Hosts per Subnet"]
        )
    
    if division_method == "By Number of Subnets":
        num_subnets = st.number_input(
            "Number of Subnets:",
            min_value=2,
            max_value=1024,
            value=4,
            help="How many subnets do you need?"
        )
        
        if st.button("Divide Network", key="divide_by_subnets"):
            try:
                with st.spinner("Calculating subnets..."):
                    time.sleep(0.2)  # Brief delay for better UX
                    result = subnet_calc.divide_network_by_subnets(parent_network, num_subnets)
                
                if 'error' not in result:
                    st.success(f"Successfully divided {parent_network} into {len(result)} subnets")
                    
                    # Create a DataFrame for better display
                    subnet_data = []
                    for subnet in result:
                        subnet_data.append({
                            "Network": subnet['network_address'],
                            "Mask": subnet['subnet_mask'],
                            "Hosts": subnet['num_hosts'],
                            "First Host": subnet['first_host'],
                            "Last Host": subnet['last_host']
                        })
                    
                    st.dataframe(pd.DataFrame(subnet_data))
                    
                    # Visualization
                    st.subheader("Subnet Visualization")
                    try:
                        # Create visualization with parent network and all subnets
                        subnet_img = create_subnet_visualization(parent_network, result)
                        if subnet_img:
                            st.image(subnet_img, use_column_width=True)
                    except Exception as vis_err:
                        st.warning(f"Could not generate subnet visualization: {str(vis_err)}")
                else:
                    st.error(f"Error: {result['error']}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        hosts_per_subnet = st.number_input(
            "Hosts per Subnet:",
            min_value=2,
            max_value=16777214,
            value=62,
            help="How many host addresses do you need in each subnet?"
        )
        
        if st.button("Divide Network", key="divide_by_hosts"):
            try:
                with st.spinner("Calculating subnets..."):
                    time.sleep(0.2)  # Brief delay for better UX
                    result = subnet_calc.divide_network_by_hosts(parent_network, hosts_per_subnet)
                
                if 'error' not in result:
                    st.success(f"Successfully created subnets with at least {hosts_per_subnet} hosts each")
                    
                    # Create a DataFrame for better display
                    subnet_data = []
                    for subnet in result:
                        subnet_data.append({
                            "Network": subnet['network_address'],
                            "Mask": subnet['subnet_mask'],
                            "Hosts": subnet['num_hosts'],
                            "First Host": subnet['first_host'],
                            "Last Host": subnet['last_host']
                        })
                    
                    st.dataframe(pd.DataFrame(subnet_data))
                    
                    # Add practical advice
                    st.info(f"""
                    **Network Planning Tip:** 
                    These subnets each support {hosts_per_subnet} hosts. Remember to account for growth by choosing a subnet that allows for additional hosts in the future.
                    """)
                else:
                    st.error(f"Error: {result['error']}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Tab 3: Host Count
with tab3:
    st.header("Find Network Size by Host Count")
    
    st.write("Determine the right network size based on the number of hosts you need.")
    
    num_hosts = st.number_input(
        "Number of Hosts Needed:",
        min_value=1,
        max_value=16777214,
        value=25,
        help="How many host IP addresses do you need in your network?"
    )
    
    if st.button("Calculate Network Size", key="calc_network_size"):
        try:
            with st.spinner("Calculating appropriate network size..."):
                time.sleep(0.2)  # Brief delay for better UX
                subnet_size = subnet_calc.get_subnet_for_hosts(num_hosts)
            
            if 'error' not in subnet_size:
                st.success(f"To accommodate {num_hosts} hosts, you need a /{subnet_size['prefix_length']} network")
                
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                # Display detailed information
                st.markdown("<div class='section-header'>Network Details</div>", unsafe_allow_html=True)
                st.markdown(f"**Recommended Prefix Length:** /{subnet_size['prefix_length']}")
                st.markdown(f"**Subnet Mask:** {subnet_size['subnet_mask']}")
                st.markdown(f"**Total Available Hosts:** {subnet_size['num_hosts']}")
                st.markdown(f"**Utilization with {num_hosts} hosts:** {round((num_hosts / subnet_size['num_hosts']) * 100, 2)}%")
                
                # Example implementation
                st.markdown("<div class='section-header'>Example Implementation</div>", unsafe_allow_html=True)
                st.markdown(f"""
                If you're using private IP space, you could implement this as:
                * **Class C:** 192.168.1.0/{subnet_size['prefix_length']}
                * **Class B:** 172.16.0.0/{subnet_size['prefix_length']}
                * **Class A:** 10.0.0.0/{subnet_size['prefix_length']}
                """)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {subnet_size['error']}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Tab 4: Subnet Size Calculator
with tab4:
    st.header("Subnet Size Calculator")
    
    st.write("Calculate detailed information about different subnet sizes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        prefix_length = st.slider(
            "Prefix Length (CIDR):",
            min_value=0,
            max_value=32,
            value=24,
            help="Select a prefix length (0-32)"
        )
    
    with col2:
        st.write("")
        st.write("")
        st.markdown(f"**Selected Prefix:** /{prefix_length}")
    
    # Calculate and display information
    if st.button("Show Subnet Details", key="show_subnet_details") or True:
        try:
            # Get subnet information
            subnet_info = subnet_calc.get_prefix_info(prefix_length)
            
            if 'error' not in subnet_info:
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                
                # Basic information
                st.markdown("<div class='section-header'>Subnet Details</div>", unsafe_allow_html=True)
                st.markdown(f"**Subnet Mask:** {subnet_info['subnet_mask']}")
                st.markdown(f"**Wildcard Mask:** {subnet_info['wildcard_mask']}")
                st.markdown(f"**Number of Hosts:** {subnet_info['num_hosts']:,}")
                st.markdown(f"**Number of Networks:** {subnet_info['num_networks']:,}")
                
                # Binary representation of the mask
                st.markdown("<div class='section-header'>Binary Representation</div>", unsafe_allow_html=True)
                binary_mask = bin(int(ipaddress.IPv4Address(subnet_info['subnet_mask'])))[2:].zfill(32)
                binary_mask_formatted = '.'.join([binary_mask[i:i+8] for i in range(0, 32, 8)])
                
                st.markdown(f"""
                **Binary Subnet Mask:** 
                <div style="font-family: monospace; background-color: #f8fafd; padding: 10px; border-radius: 4px; margin-top: 5px;">
                {binary_mask_formatted}
                </div>
                """, unsafe_allow_html=True)
                
                # Usage examples
                st.markdown("<div class='section-header'>Usage Examples</div>", unsafe_allow_html=True)
                st.markdown(f"""
                * **Class A Private Network:** 10.0.0.0/{prefix_length}
                * **Class B Private Network:** 172.16.0.0/{prefix_length}
                * **Class C Private Network:** 192.168.1.0/{prefix_length}
                """)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {subnet_info['error']}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
# Footer with helpful tips
st.markdown("""
<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eaeff5; text-align: center; color: #6c757d; font-size: 0.9rem;">
IP Subnet Calculator - A helpful tool for network engineers and IT professionals
</div>
""", unsafe_allow_html=True)
