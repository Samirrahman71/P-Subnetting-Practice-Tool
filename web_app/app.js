/**
 * IP Subnet Calculator
 * A mobile-friendly web application for IP subnet calculations
 */

// Show the selected tab and hide others
function showTab(tabId) {
    // Hide all content
    const contents = document.querySelectorAll('.content');
    contents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Deactivate all tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected content and activate tab
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// Toggle between subnet methods
function toggleSubnetMethod() {
    const method = document.getElementById('subnet-method').value;
    if (method === 'num-subnets') {
        document.getElementById('num-subnets-group').style.display = 'block';
        document.getElementById('prefix-length-group').style.display = 'none';
    } else {
        document.getElementById('num-subnets-group').style.display = 'none';
        document.getElementById('prefix-length-group').style.display = 'block';
    }
}

// Validate IP address with CIDR or netmask
function validateNetwork(networkStr) {
    // CIDR notation (e.g., 192.168.1.0/24)
    const cidrPattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\/(0|[1-9]|[12][0-9]|3[0-2])$/;
    
    // IP with netmask (e.g., 192.168.1.0 255.255.255.0)
    const maskPattern = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\s+(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/;
    
    if (cidrPattern.test(networkStr)) {
        const parts = networkStr.split('/');
        return isValidIP(parts[0]) && parseInt(parts[1]) >= 0 && parseInt(parts[1]) <= 32;
    } else if (maskPattern.test(networkStr)) {
        const parts = networkStr.split(/\s+/);
        return isValidIP(parts[0]) && isValidNetmask(parts[1]);
    }
    
    return false;
}

// Validate IP address
function isValidIP(ip) {
    const parts = ip.split('.');
    if (parts.length !== 4) return false;
    
    for (let i = 0; i < 4; i++) {
        const octet = parseInt(parts[i]);
        if (isNaN(octet) || octet < 0 || octet > 255) return false;
    }
    
    return true;
}

// Validate subnet mask
function isValidNetmask(mask) {
    const parts = mask.split('.');
    if (parts.length !== 4) return false;
    
    // Convert to binary string
    let binary = '';
    for (let i = 0; i < 4; i++) {
        const octet = parseInt(parts[i]);
        if (isNaN(octet) || octet < 0 || octet > 255) return false;
        binary += octet.toString(2).padStart(8, '0');
    }
    
    // Valid netmasks have all 1s followed by all 0s
    return /^1*0*$/.test(binary);
}

// Check if a number is a power of 2
function isPowerOfTwo(n) {
    return n > 0 && (n & (n - 1)) === 0;
}

// Calculate and display network information
function calculateNetworkInfo() {
    const networkStr = document.getElementById('network').value.trim();
    const errorElement = document.getElementById('network-error');
    const resultElement = document.getElementById('network-result');
    const tableElement = document.getElementById('network-table');
    
    // Validate input
    if (!validateNetwork(networkStr)) {
        errorElement.style.display = 'block';
        resultElement.style.display = 'none';
        return;
    }
    
    errorElement.style.display = 'none';
    
    try {
        // Calculate network information
        const info = getNetworkInfo(networkStr);
        
        // Display results
        tableElement.innerHTML = '';
        for (const [key, value] of Object.entries(info)) {
            const row = document.createElement('tr');
            const keyCell = document.createElement('td');
            const valueCell = document.createElement('td');
            
            keyCell.textContent = key;
            valueCell.textContent = value;
            
            row.appendChild(keyCell);
            row.appendChild(valueCell);
            tableElement.appendChild(row);
        }
        
        resultElement.style.display = 'block';
    } catch (error) {
        errorElement.textContent = `Error: ${error.message}`;
        errorElement.style.display = 'block';
        resultElement.style.display = 'none';
    }
}

// Calculate and display subnet information
function calculateSubnet() {
    const networkStr = document.getElementById('subnet-network').value.trim();
    const method = document.getElementById('subnet-method').value;
    const numSubnets = parseInt(document.getElementById('num-subnets').value);
    const prefixLength = parseInt(document.getElementById('prefix-length').value);
    
    const networkError = document.getElementById('subnet-network-error');
    const numSubnetsError = document.getElementById('num-subnets-error');
    const prefixLengthError = document.getElementById('prefix-length-error');
    const resultElement = document.getElementById('subnet-result');
    const tableElement = document.getElementById('subnet-table');
    const summaryElement = document.getElementById('subnet-summary');
    
    // Reset errors
    networkError.style.display = 'none';
    numSubnetsError.style.display = 'none';
    prefixLengthError.style.display = 'none';
    
    // Validate network
    if (!validateNetwork(networkStr)) {
        networkError.style.display = 'block';
        resultElement.style.display = 'none';
        return;
    }
    
    try {
        let subnets;
        const networkInfo = getNetworkInfo(networkStr);
        const originalPrefix = parseInt(networkInfo['Prefix Length']);
        
        if (method === 'num-subnets') {
            // Validate number of subnets
            if (!isPowerOfTwo(numSubnets)) {
                numSubnetsError.style.display = 'block';
                resultElement.style.display = 'none';
                return;
            }
            
            // Calculate bits needed for subnets
            const bitsNeeded = Math.log2(numSubnets);
            const newPrefix = originalPrefix + bitsNeeded;
            
            if (newPrefix > 32) {
                numSubnetsError.textContent = `Cannot create ${numSubnets} subnets from a /${originalPrefix} network.`;
                numSubnetsError.style.display = 'block';
                resultElement.style.display = 'none';
                return;
            }
            
            subnets = calculateSubnets(networkStr, 0, newPrefix);
            summaryElement.textContent = `Dividing ${networkStr} into ${numSubnets} subnets (/${newPrefix})`;
        } else {
            // Validate prefix length
            if (prefixLength <= originalPrefix) {
                prefixLengthError.textContent = `New prefix must be larger than ${originalPrefix}.`;
                prefixLengthError.style.display = 'block';
                resultElement.style.display = 'none';
                return;
            }
            
            if (prefixLength > 32) {
                prefixLengthError.textContent = 'Prefix must be 32 or less.';
                prefixLengthError.style.display = 'block';
                resultElement.style.display = 'none';
                return;
            }
            
            subnets = calculateSubnets(networkStr, 0, prefixLength);
            const numSubnets = Math.pow(2, prefixLength - originalPrefix);
            summaryElement.textContent = `Dividing ${networkStr} into ${numSubnets} subnets (/${prefixLength})`;
        }
        
        // Display results
        tableElement.innerHTML = '<tr><td><b>Subnet</b></td><td><b>Network</b></td><td><b>Broadcast</b></td><td><b>Hosts</b></td></tr>';
        
        for (const subnet of subnets) {
            const row = document.createElement('tr');
            
            const subnetCell = document.createElement('td');
            subnetCell.textContent = subnet.cidr;
            
            const networkCell = document.createElement('td');
            networkCell.textContent = subnet.networkAddress;
            
            const broadcastCell = document.createElement('td');
            broadcastCell.textContent = subnet.broadcastAddress;
            
            const hostsCell = document.createElement('td');
            hostsCell.textContent = subnet.numHosts;
            
            row.appendChild(subnetCell);
            row.appendChild(networkCell);
            row.appendChild(broadcastCell);
            row.appendChild(hostsCell);
            
            tableElement.appendChild(row);
        }
        
        resultElement.style.display = 'block';
    } catch (error) {
        networkError.textContent = `Error: ${error.message}`;
        networkError.style.display = 'block';
        resultElement.style.display = 'none';
    }
}

// Calculate and display subnet for required hosts
function calculateForHosts() {
    const numHosts = parseInt(document.getElementById('num-hosts').value);
    const baseNetwork = document.getElementById('base-network').value.trim();
    
    const hostsError = document.getElementById('num-hosts-error');
    const networkError = document.getElementById('base-network-error');
    const resultElement = document.getElementById('hosts-result');
    const tableElement = document.getElementById('hosts-table');
    const summaryElement = document.getElementById('hosts-summary');
    
    // Reset errors
    hostsError.style.display = 'none';
    networkError.style.display = 'none';
    
    // Validate hosts
    if (isNaN(numHosts) || numHosts <= 0) {
        hostsError.style.display = 'block';
        resultElement.style.display = 'none';
        return;
    }
    
    try {
        // Calculate required bits for hosts
        const hostBits = Math.ceil(Math.log2(numHosts + 2)); // +2 for network and broadcast
        const prefixLength = 32 - hostBits;
        
        if (prefixLength < 0) {
            hostsError.textContent = `Cannot accommodate ${numHosts} hosts in an IPv4 network.`;
            hostsError.style.display = 'block';
            resultElement.style.display = 'none';
            return;
        }
        
        const maxHosts = Math.pow(2, hostBits) - 2;
        
        // Format the summary message
        summaryElement.innerHTML = `For ${numHosts} hosts, you need a /${prefixLength} subnet<br>`;
        summaryElement.innerHTML += `Subnet mask: ${prefixToDottedDecimal(prefixLength)}<br>`;
        summaryElement.innerHTML += `This subnet can accommodate ${maxHosts} hosts`;
        
        // If base network provided, calculate network details
        if (baseNetwork) {
            if (!isValidIP(baseNetwork)) {
                networkError.style.display = 'block';
                tableElement.innerHTML = '';
                resultElement.style.display = 'block';
                return;
            }
            
            const networkStr = `${baseNetwork}/${prefixLength}`;
            const info = getNetworkInfo(networkStr);
            
            // Display network details
            tableElement.innerHTML = '';
            for (const [key, value] of Object.entries(info)) {
                const row = document.createElement('tr');
                const keyCell = document.createElement('td');
                const valueCell = document.createElement('td');
                
                keyCell.textContent = key;
                valueCell.textContent = value;
                
                row.appendChild(keyCell);
                row.appendChild(valueCell);
                tableElement.appendChild(row);
            }
        } else {
            tableElement.innerHTML = '';
        }
        
        resultElement.style.display = 'block';
    } catch (error) {
        hostsError.textContent = `Error: ${error.message}`;
        hostsError.style.display = 'block';
        resultElement.style.display = 'none';
    }
}

// Calculate and display supernet information
function calculateSupernet() {
    const networksText = document.getElementById('networks').value.trim();
    const errorElement = document.getElementById('networks-error');
    const resultElement = document.getElementById('supernet-result');
    const tableElement = document.getElementById('supernet-table');
    const summaryElement = document.getElementById('supernet-summary');
    
    // Reset error
    errorElement.style.display = 'none';
    
    // Get networks
    const networks = networksText.split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
    
    if (networks.length < 2) {
        errorElement.textContent = 'Please enter at least two networks.';
        errorElement.style.display = 'block';
        resultElement.style.display = 'none';
        return;
    }
    
    // Validate each network
    for (const network of networks) {
        if (!validateNetwork(network)) {
            errorElement.textContent = `Invalid network: ${network}`;
            errorElement.style.display = 'block';
            resultElement.style.display = 'none';
            return;
        }
    }
    
    try {
        // Calculate supernet (simple implementation - works for adjacent networks)
        const parsedNetworks = networks.map(network => {
            const info = getNetworkInfo(network);
            return {
                network: info['Network Address'],
                prefixLength: parseInt(info['Prefix Length']),
                intValue: ipToInt(info['Network Address'])
            };
        });
        
        // Sort networks by address
        parsedNetworks.sort((a, b) => a.intValue - b.intValue);
        
        // Find the smallest prefix that contains all networks
        const firstNetwork = parsedNetworks[0];
        const lastNetwork = parsedNetworks[parsedNetworks.length - 1];
        const lastBroadcast = ipToInt(getNetworkInfo(networks[networks.length - 1])['Broadcast Address']);
        
        // Find common prefix bits
        const diff = lastNetwork.intValue - firstNetwork.intValue;
        const diffBits = diff === 0 ? 0 : 32 - Math.floor(Math.log2(lastBroadcast - firstNetwork.intValue + 1));
        const commonPrefix = Math.min(diffBits, firstNetwork.prefixLength);
        
        if (commonPrefix <= 0) {
            errorElement.textContent = 'No common supernet found for these networks.';
            errorElement.style.display = 'block';
            resultElement.style.display = 'none';
            return;
        }
        
        // Create supernet
        const supernet = `${firstNetwork.network}/${commonPrefix}`;
        const supernetInfo = getNetworkInfo(supernet);
        
        // Display summary
        summaryElement.textContent = `Supernet that contains all provided networks: ${supernet}`;
        
        // Display results
        tableElement.innerHTML = '';
        for (const [key, value] of Object.entries(supernetInfo)) {
            const row = document.createElement('tr');
            const keyCell = document.createElement('td');
            const valueCell = document.createElement('td');
            
            keyCell.textContent = key;
            valueCell.textContent = value;
            
            row.appendChild(keyCell);
            row.appendChild(valueCell);
            tableElement.appendChild(row);
        }
        
        resultElement.style.display = 'block';
    } catch (error) {
        errorElement.textContent = `Error: ${error.message}`;
        errorElement.style.display = 'block';
        resultElement.style.display = 'none';
    }
}

// Helper function to convert prefix length to dotted decimal
function prefixToDottedDecimal(prefix) {
    const mask = ~(0xffffffff >>> prefix) >>> 0;
    return [(mask >>> 24) & 0xff, 
            (mask >>> 16) & 0xff, 
            (mask >>> 8) & 0xff, 
            mask & 0xff].join('.');
}

// Helper function to convert dotted decimal to prefix length
function dottedDecimalToPrefix(mask) {
    const parts = mask.split('.');
    let binary = '';
    for (let i = 0; i < 4; i++) {
        binary += parseInt(parts[i]).toString(2).padStart(8, '0');
    }
    return binary.split('0')[0].length;
}

// Helper function to convert IP to integer
function ipToInt(ip) {
    const parts = ip.split('.');
    return ((parseInt(parts[0], 10) << 24) |
            (parseInt(parts[1], 10) << 16) |
            (parseInt(parts[2], 10) << 8) |
            parseInt(parts[3], 10)) >>> 0;
}

// Helper function to convert integer to IP
function intToIp(int) {
    return [
        (int >>> 24) & 0xff,
        (int >>> 16) & 0xff,
        (int >>> 8) & 0xff,
        int & 0xff
    ].join('.');
}

// Calculate network information
function getNetworkInfo(networkStr) {
    let ip, prefixLength;
    
    // Parse CIDR notation
    if (networkStr.includes('/')) {
        const parts = networkStr.split('/');
        ip = parts[0];
        prefixLength = parseInt(parts[1]);
    } 
    // Parse IP with netmask
    else if (networkStr.includes(' ')) {
        const parts = networkStr.split(/\s+/);
        ip = parts[0];
        prefixLength = dottedDecimalToPrefix(parts[1]);
    } else {
        throw new Error('Invalid network format');
    }
    
    const ipInt = ipToInt(ip);
    const mask = ~(0xffffffff >>> prefixLength) >>> 0;
    const networkAddress = intToIp((ipInt & mask) >>> 0);
    const broadcastAddress = intToIp((ipInt | ~mask) >>> 0);
    const wildcardMask = intToIp((~mask) >>> 0);
    const subnetMask = intToIp(mask);
    
    // Calculate number of hosts
    let numHosts;
    if (prefixLength >= 31) {
        numHosts = Math.pow(2, 32 - prefixLength);
    } else {
        numHosts = Math.pow(2, 32 - prefixLength) - 2;
    }
    
    // Calculate IP range
    const firstHost = (ipInt & mask) + (prefixLength >= 31 ? 0 : 1);
    const lastHost = (ipInt | ~mask) - (prefixLength >= 31 ? 0 : 1);
    const ipRange = `${intToIp(firstHost)} - ${intToIp(lastHost)}`;
    
    // Determine network class
    let networkClass;
    const firstOctet = parseInt(ip.split('.')[0]);
    if (firstOctet < 128) networkClass = 'A';
    else if (firstOctet < 192) networkClass = 'B';
    else if (firstOctet < 224) networkClass = 'C';
    else if (firstOctet < 240) networkClass = 'D (Multicast)';
    else networkClass = 'E (Reserved)';
    
    return {
        'Network Address': networkAddress,
        'Broadcast Address': broadcastAddress,
        'Subnet Mask': subnetMask,
        'Wildcard Mask': wildcardMask,
        'Prefix Length': prefixLength.toString(),
        'Network Class': networkClass,
        'Number of Hosts': numHosts.toString(),
        'IP Range': ipRange,
        'CIDR Notation': `${networkAddress}/${prefixLength}`
    };
}

// Calculate subnets
function calculateSubnets(networkStr, numSubnets, newPrefixLength) {
    const info = getNetworkInfo(networkStr);
    const networkAddress = info['Network Address'];
    const originalPrefix = parseInt(info['Prefix Length']);
    
    // Calculate new prefix length if number of subnets is provided
    if (numSubnets > 0) {
        const bitsNeeded = Math.log2(numSubnets);
        newPrefixLength = originalPrefix + bitsNeeded;
    }
    
    // Validate new prefix length
    if (newPrefixLength <= originalPrefix) {
        throw new Error(`New prefix length must be greater than ${originalPrefix}`);
    }
    
    if (newPrefixLength > 32) {
        throw new Error('Prefix length cannot be greater than 32');
    }
    
    const networkInt = ipToInt(networkAddress);
    const numSubnetsToCreate = Math.pow(2, newPrefixLength - originalPrefix);
    const subnetSize = Math.pow(2, 32 - newPrefixLength);
    
    const subnets = [];
    for (let i = 0; i < numSubnetsToCreate; i++) {
        const subnetInt = networkInt + (i * subnetSize);
        const subnetAddress = intToIp(subnetInt);
        const broadcastInt = subnetInt + subnetSize - 1;
        const broadcastAddress = intToIp(broadcastInt);
        
        // Calculate number of hosts
        let numHosts;
        if (newPrefixLength >= 31) {
            numHosts = Math.pow(2, 32 - newPrefixLength);
        } else {
            numHosts = Math.pow(2, 32 - newPrefixLength) - 2;
        }
        
        subnets.push({
            cidr: `${subnetAddress}/${newPrefixLength}`,
            networkAddress: subnetAddress,
            broadcastAddress: broadcastAddress,
            numHosts: numHosts
        });
    }
    
    return subnets;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Show default tab
    showTab('network-info');
    
    // Set up event listeners for Enter key in input fields
    document.getElementById('network').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') calculateNetworkInfo();
    });
    
    document.getElementById('subnet-network').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') calculateSubnet();
    });
    
    document.getElementById('num-hosts').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') calculateForHosts();
    });
    
    document.getElementById('base-network').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') calculateForHosts();
    });
});
