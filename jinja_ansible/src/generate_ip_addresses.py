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

    return interface_ips, loopback_ips