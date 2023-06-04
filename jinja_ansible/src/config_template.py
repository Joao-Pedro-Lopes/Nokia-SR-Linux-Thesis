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
    for neighbors_dict in neighbors.values(): # Main node
        #for neighbor_dict in neighbors_dict.values(): # Neighbor node -- now neighbors is for the specific node (don't need this)
        peer = {
            'peer-as': neighbors_dict["as"],
            'peer-address': neighbors_dict["ip"],
        }
        peers.append(peer)

    return {'ebgp': ebgp, 'peers': peers}

def config_ibgp(node, as_numbers, loopback_ips, neighbors):
    ibgp = {
        'as-number': "XXX",
    }

    peers = []
    for neighbors_dict in neighbors.values(): # Main node
        #for neighbor_dict in neighbors_dict.values(): # Neighbor node -- now neighbors is for the specific node (don't need this)
        peer = {
            'peer-as': "YYY",
            'peer-address': "ZZZ",
            'local-address': loopback_ips[node].split("/")[0],
        }
        peers.append(peer)

    return {'ibgp': ibgp, 'peers': peers}

"""def config_template(config_type, node, config):
    print(config_type)
    print(node)
    print(config)
    if config_type == 'interfaces':
        return {
            'node': node,
            'interface-name': config['config']['vars'].get('interface-name', ''),
            'ip-address-p2p': config['config']['vars'].get('ip-address-p2p', ''),
            'ip-address-loopback': config['config']['vars'].get('ip-address-loopback', '')
        }
    elif config_type == 'ebgp':
        return {
            'node': node,
            'autonomous-system': config['config']['vars'].get('autonomous-system', ''),
            'router-id': config['config']['vars'].get('router-id', ''),
            'peer-as': config['config']['vars'].get('peer-as', ''),
            'peer-address': config['config']['vars'].get('peer-address', '')
        }
    else:
        return None"""