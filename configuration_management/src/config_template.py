def config_interfaces(node, interface_ips):
    interfaces = []
    for intf, ip in interface_ips[node].items():
        # Create a dictionary for each interface
        interface = {
            'interface-name': f'ethernet-{intf.replace("e", "")}',
            'ip-address-p2p': ip,
        }
        interfaces.append(interface)
    
    return {'interfaces': interfaces}

def config_ebgp(node, as_numbers, loopback_ips, neighbors):
    ebgp = {
        'autonomous-system': as_numbers[node],
        'router-id': loopback_ips[node].split("/")[0],
    }

    peers = []
    for neighbors_dict in neighbors.values():
        peer = {
            'peer-as': neighbors_dict["as"],
            'peer-address': neighbors_dict["ip"],
        }
        peers.append(peer)

    return {'ebgp': ebgp, 'peers': peers}

def config_ibgp(node, as_numbers, loopback_ips, neighbors, ibgp_as_number):
    ibgp = {
        'as-number': ibgp_as_number,
    }

    peers = []
    for neighbors_dict in neighbors.values():
        peer = {
            'peer-as': ibgp_as_number,
            'peer-address': neighbors_dict["loopback_ip"],
            'local-address': loopback_ips[node].split("/")[0],
        }
        peers.append(peer)

    return {'ibgp': ibgp, 'peers': peers}

def config_mac_vrf(node, interface_mac_vrf, vrfs):
    # Create a dictionary for each interface
    interfaces = []
    for intf, vrf_ids in interface_mac_vrf[node].items():
        for vrf_id in vrf_ids:
            interface = {
                'interface-name': f'ethernet-{intf.replace("e", "")}',
                'vlan_id': vrfs[vrf_id]['vlan_id'],
                'vxlan_name': vrfs[vrf_id]['vxlan_name'],
                'vxlan_interface': vrfs[vrf_id]['vlan_id'] + 1,
                'vni': vrfs[vrf_id]['vlan_id'] + 1,
                'vrf_name': vrfs[vrf_id]['vrf_name'],
            }
            interfaces.append(interface)
    
    return {'interfaces': interfaces}
