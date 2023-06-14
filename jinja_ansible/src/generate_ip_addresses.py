import ipaddress

def generate_ip_addresses(data):
    # Starting IP addresses
    p2p_subnet = ipaddress.ip_network(data['topology']['defaults']['env']['P2P_IP_SUBNET'])
    loopback_subnet = ipaddress.ip_network(data['topology']['defaults']['env']['LOOPBACK_IP_SUBNET'])
    p2p_subnets = p2p_subnet.subnets(new_prefix=30)
    loopback_addresses = loopback_subnet.hosts()

    # Generate interface IP addresses for each node
    interface_ips = {}  # node -> interface -> ip
    interface_mac_vrf = {}  # dictionary for servers
    loopback_ips = {}  # node -> ip
    neighbors_bgp = {}  # node -> [neighbor1, neighbor2, ...]
    neighbors_ibgp = {}  # node -> [neighbor1, neighbor2, ...]

    for link in data['topology']['links']:
        # Parse endpoints
        node1, intf1 = link['endpoints'][0].split(':')
        node2, intf2 = link['endpoints'][1].split(':')

        intf1 = intf1.replace("-", "/")
        intf2 = intf2.replace("-", "/")

        # Get subnet for this link
        subnet = next(p2p_subnets)
        ip1, ip2 = subnet.hosts()
        
        # Save IP addresses - check if nodes exist before setting interfaces
        if data['topology']['nodes'].get(node1, {}).get('config', {}).get('vars', {}).get('type', '') in ['leaf', 'spine', 'super-spine'] and data['topology']['nodes'].get(node2, {}).get('config', {}).get('vars', {}).get('type', '') in ['leaf', 'spine', 'super-spine']:
            # The if above removes interfaces that connect to servers
            if node1 not in interface_ips:
                interface_ips[node1] = {}
            if node2 not in interface_ips:
                interface_ips[node2] = {}
            interface_ips[node1][intf1] = f"{ip1}/30"
            interface_ips[node2][intf2] = f"{ip2}/30"
        else:
            # If not, save IPs to interface_mac_vrf
            if data['topology']['nodes'].get(node1, {}).get('config', {}).get('vars', {}).get('type', '') in ['leaf', 'spine', 'super-spine']:
                if node1 not in interface_mac_vrf:
                    interface_mac_vrf[node1] = {}
                interface_mac_vrf[node1] = intf1
            if data['topology']['nodes'].get(node2, {}).get('config', {}).get('vars', {}).get('type', '') in ['leaf', 'spine', 'super-spine']:
                if node2 not in interface_mac_vrf:
                    interface_mac_vrf[node2] = {}
                interface_mac_vrf[node2] = intf2
            #interface_mac_vrf[node1][intf1] = f"{ip1}/30"
            #interface_mac_vrf[node2][intf2] = f"{ip2}/30"

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
            if node1 not in neighbors_bgp:
                neighbors_bgp[node1] = {}
            neighbors_bgp[node1][node2] = {"ip": f"{ip2}"}

            if node1 not in neighbors_ibgp:
                neighbors_ibgp[node1] = {}
            neighbors_ibgp[node1][node2] = {"loopback_ip": loopback_ips[node2].split("/")[0]}

        if node2_type in ['leaf', 'spine', 'super-spine']:
            if node2 not in neighbors_bgp:
                neighbors_bgp[node2] = {}
            neighbors_bgp[node2][node1] = {"ip": f"{ip1}"}

            if node2 not in neighbors_ibgp:
                neighbors_ibgp[node2] = {}
            neighbors_ibgp[node2][node1] = {"loopback_ip": loopback_ips[node1].split("/")[0]}

    return interface_ips, interface_mac_vrf, loopback_ips, neighbors_bgp, neighbors_ibgp