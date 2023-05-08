def bgp_generator(interface_configs, node_name, node_data, individual):
    config = {}
    if (individual):
        config[node_name] = {}
        config[node_name]['network-instance'] = []
        config[node_name]['network-instance'].append({})
    else:
        config[node_name] = interface_configs[node_name]


    peer_groups = [peer_g.strip() for peer_g in node_data['config']['vars']['bgp-peer-group'].split(',')]
    neighbors = [n.strip() for n in node_data['config']['vars']['bgp-neighbor'].split(',')]

    bgp_underlay_template = {
        'autonomous-system': node_data['config']['vars']['as'],
        'router-id': node_data['config']['vars']['bgp-router-id'],
        'group': [
            {
                'group-name': node_data['config']['vars']['bgp-group'],
                'export-policy': 'all', #node_data['config']['vars']['bgp-export-policy']
                'import-policy': 'all', #node_data['config']['vars']['bgp-import-policy']
                'ipv4-unicast': {
                    'admin-state': 'enable'
                },
            }
        ],
        'neighbor': []
    }

    peer_as = node_data['config']['vars']['bgp-peer-as']
    peer_autonomous_systems = []
    if isinstance(peer_as, int):
        bgp_underlay_template['group'][0]['peer-as'] = peer_as
    elif isinstance(peer_as, str):
        peer_autonomous_systems = [peer_as.strip() for peer_as in peer_as.split(',')]

    config[node_name]['network-instance'][0]['name'] = "default" #FIXME: perguntar Sérgio
    config[node_name]['network-instance'][0]['protocols'] = {}
    config[node_name]['network-instance'][0]['protocols']['bgp'] = bgp_underlay_template


    if peer_autonomous_systems != []:
        for i, (peer_autonomous_system, peer_group, neighbor) in enumerate(zip(peer_autonomous_systems, peer_groups, neighbors)):
            bgp_neighbor_template = {
                'peer-address': neighbor,
                'peer-as': int(peer_autonomous_system),
                'peer-group': peer_group
            }

            config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'].append(bgp_neighbor_template)
    else:
        for i, (peer_group, neighbor) in enumerate(zip(peer_groups, neighbors)):
            bgp_neighbor_template = {
                'peer-address': neighbor,
                'peer-group': peer_group
            }

            config[node_name]['network-instance'][0]['protocols']['bgp']['neighbor'].append(bgp_neighbor_template)
    
    return config