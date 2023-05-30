import ipaddress

def generate_ip_addresses(data):
    # Starting IP addresses
    p2p_subnet = ipaddress.ip_network('192.168.11.0/24')
    loopback_subnet = ipaddress.ip_network('10.0.0.0/24')
    p2p_subnets = p2p_subnet.subnets(new_prefix=30)
    loopback_addresses = loopback_subnet.hosts()

    # Generate interface IP addresses for each node
    interface_ips = {}  # node -> interface -> ip
    loopback_ips = {}  # node -> ip
    neighbors = {}  # node -> [neighbor1, neighbor2, ...]
    for link in data['topology']['links']:
        # Parse endpoints
        node1, intf1 = link['endpoints'][0].split(':')
        node2, intf2 = link['endpoints'][1].split(':')

        intf1 = intf1.replace("-", "/")
        intf2 = intf2.replace("-", "/")

        # Get subnet for this link
        subnet = next(p2p_subnets)
        ip1, ip2 = subnet.hosts()

        # Save IP addresses
        if node1 not in interface_ips:
            interface_ips[node1] = {}
        if node2 not in interface_ips:
            interface_ips[node2] = {}
        interface_ips[node1][intf1] = f"{ip1}/30"
        interface_ips[node2][intf2] = f"{ip2}/30"

        # Save loopback addresses
        if node1 not in loopback_ips:
            loopback_ips[node1] = f"{next(loopback_addresses)}/32"
        if node2 not in loopback_ips:
            loopback_ips[node2] = f"{next(loopback_addresses)}/32"

        # Save neighbors
        if 'config' in data['topology']['nodes'][node1] and 'config' in data['topology']['nodes'][node2]:
            node1_type = data['topology']['nodes'][node1]['config']['vars']['type']
            node2_type = data['topology']['nodes'][node2]['config']['vars']['type']
        else:
            continue

        if node1_type in ['leaf', 'spine', 'super-spine']:
            if node1 not in neighbors:
                neighbors[node1] = {}
            #neighbors[node1].append(node2) -- uncomment to check which node is being added
            #neighbors[node1].append({node2: f"{ip2}"})
            neighbors[node1][node2] = {"ip": f"{ip2}"}
        if node2_type in ['leaf', 'spine', 'super-spine']:
            if node2 not in neighbors:
                neighbors[node2] = {}
            #neighbors[node2].append(node1) -- uncomment to check which node is being added
            #neighbors[node2].append({node1: f"{ip1}"})
            neighbors[node2][node1] = {"ip": f"{ip1}"}

    return interface_ips, loopback_ips, neighbors